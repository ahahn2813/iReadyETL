import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re
import openpyxl
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# clean the reading data, prepare for feature engineering
def clean_iready_read(iready_read, term):
    iready_read.columns = iready_read.columns.str.lower().str.replace(" ", "_")
    drop_rel_list = list(iready_read.columns[iready_read.columns.str.contains("relative")])
    drop_list = drop_rel_list + ["projection_if_student_achieves_typical_growth", "projection_if_student_achieves_stretch_growth", "proficiency_if_student_shows_no_additional_growth", "lexile_range", "date", "rush_flag"]
    iready_read = iready_read.drop(columns=drop_list)
    list_placement = list(iready_read.columns[iready_read.columns.str.contains("placement")])
    for col in list_placement:
        iready_read.loc[iready_read[col] == "Surpassed Level", col] = "S"
        iready_read.loc[iready_read[col] == "Max Score", col] = "M"
        iready_read.loc[iready_read[col] == "Not Assessed", col] = "NA"
        iready_read.loc[iready_read[col].str.startswith("Gr"), col] = "Gr " + iready_read.loc[iready_read[col].str.startswith("Gr"), col].str[-1]
    iready_read.columns = ["student", "score", "Overall_Place","Ph_A", "Ph_Place", "HFW", "V", "Comp_Overall", "Comp-L", "Comp-I", "annual_typical_growth_measure", "annual_stretch_growth_measure", "Lexile", "Percentile"]
    if "fa" in term.lower():
        iready_read["growth_score_goal"] = iready_read["score"] + iready_read["annual_typical_growth_measure"]
        iready_read["stretch_score_goal"] = iready_read["score"] + iready_read["annual_stretch_growth_measure"]
    iready_read = iready_read.drop(columns=["annual_typical_growth_measure", "annual_stretch_growth_measure"])
    iready_read = iready_read.add_prefix("iReady_" + term + "_")
    return iready_read

# clean the math data, prepare for feature engineering
def clean_iready_math(iready_math, term):
    iready_math.columns = iready_math.columns.str.lower().str.replace(" ", "_")
    drop_list = list(iready_math.columns[iready_math.columns.str.contains("relative|quantile|projection|proficiency|date|flag|language", regex = True)])
    iready_math = iready_math.drop(columns=drop_list)
    list_placement = list(iready_math.columns[iready_math.columns.str.contains("placement")])
    for col in list_placement:
        iready_math.loc[iready_math[col].str.startswith("Gr"), col] = "Gr " + iready_math.loc[iready_math[col].str.startswith("Gr"), col].str[-1]
    iready_math.columns = ["student", "score", "Overall_Place","Num_Op", "AA", "MD", "G", "annual_typical_growth_measure", "annual_stretch_growth_measure", "percentile"]
    if "fa" in term.lower():
        iready_math["growth_score_goal"] = iready_math["score"] + iready_math["annual_typical_growth_measure"]
        iready_math["stretch_score_goal"] = iready_math["score"] + iready_math["annual_stretch_growth_measure"]
    iready_math = iready_math.drop(columns=["annual_typical_growth_measure", "annual_stretch_growth_measure"])
    col_to_move = iready_math.pop('percentile')
    new_index = iready_math.columns.get_loc("Overall_Place") + 1
    iready_math.insert(new_index, "percentile", col_to_move)
    iready_math = iready_math.add_prefix("iReady_" + term + "_")
    return iready_math

# complete feature engineering: determin amount of growth, whether typical and stretch goals were met, aesthetic changes
def merge_engineer(data_dict, subject):
    data_list = list(data_dict.values())
    term_list = list(data_dict.keys())
    term_list = [term.upper() for term in term_list]

    for i in range(len(data_list)):
        if subject == "Reading":
            data_list[i] = clean_iready_read(data_list[i], term_list[i])
        else:
            data_list[i] = clean_iready_math(data_list[i], term_list[i])
    if len(term_list) == 3:
        #merge winter on all students
        data_list[0].loc[:,"spacer_0"] = "NAN"
        merge_winter = pd.merge(data_list[0].rename(columns = {"iReady_"+term_list[0]+"_student":"student"}), data_list[1].rename(columns={"iReady_"+term_list[1]+"_student":"student"}), how = "outer", on = "student")
        #feature engineer for whether met growth goals
        merge_winter.loc[merge_winter["iReady_" + term_list[1]+ "_score"]>= merge_winter["iReady_" + term_list[0]+ "_growth_score_goal"], "iReady_" + term_list[1]+ "_typical_growth"] = "YES"
        merge_winter.loc[merge_winter["iReady_" + term_list[1]+ "_score"]< merge_winter["iReady_" + term_list[0]+ "_growth_score_goal"], "iReady_" + term_list[1]+ "_typical_growth"] = "NO"
        merge_winter.loc[merge_winter["iReady_" + term_list[1]+ "_score"]>= merge_winter["iReady_" + term_list[0]+ "_stretch_score_goal"], "iReady_" + term_list[1]+ "_stretch_growth"] = "YES"
        merge_winter.loc[merge_winter["iReady_" + term_list[1]+ "_score"]< merge_winter["iReady_" + term_list[0]+ "_stretch_score_goal"], "iReady_" + term_list[1]+ "_stretch_growth"] = "NO"
        #how much up/down
        merge_winter.loc[:, "iReady_" + term_list[1]+ "_growth_amount"] = merge_winter.loc[:,"iReady_" + term_list[1]+ "_score"] - merge_winter.loc[:,"iReady_" + term_list[0]+ "_score"]
        merge_winter.loc[:,"spacer_1"] = "NAN"

        #merge spring on all students
        merge_spring = pd.merge(merge_winter, data_list[2].rename(columns={"iReady_"+term_list[2]+"_student":"student"}), how = "outer", on = "student")
        #feature engineer for whether met growth goals
        merge_spring.loc[merge_spring["iReady_" + term_list[2]+ "_score"]>= merge_spring["iReady_" + term_list[0]+ "_growth_score_goal"], "iReady_" + term_list[2]+ "_typical_growth"] = "YES"
        merge_spring.loc[merge_spring["iReady_" + term_list[2]+ "_score"]< merge_spring["iReady_" + term_list[0]+ "_growth_score_goal"], "iReady_" + term_list[2]+ "_typical_growth"] = "NO"
        merge_spring.loc[merge_spring["iReady_" + term_list[2]+ "_score"]>= merge_spring["iReady_" + term_list[0]+ "_stretch_score_goal"], "iReady_" + term_list[2]+ "_stretch_growth"] = "YES"
        merge_spring.loc[merge_spring["iReady_" + term_list[2]+ "_score"]< merge_spring["iReady_" + term_list[0]+ "_stretch_score_goal"], "iReady_" + term_list[2]+ "_stretch_growth"] = "NO"
        #how much up/down from winter
        merge_spring.loc[:, "iReady_" + term_list[1]+ "_to_" + term_list[2]+ "_growth_amount"] = merge_spring.loc[:,"iReady_" + term_list[2]+ "_score"] - merge_spring.loc[:,"iReady_" + term_list[1]+ "_score"]
        #how much up/down from fall
        merge_spring.loc[:, "iReady_" + term_list[0]+ "_to_" + term_list[2]+ "_growth_amount"] = merge_spring.loc[:,"iReady_" + term_list[2]+ "_score"] - merge_spring.loc[:,"iReady_" + term_list[0]+ "_score"]
        #move lexile between two growth columns for aesthetic
        if subject == "Reading":
            col_to_move = merge_spring.pop("iReady_" + term_list[1] + '_Lexile')
            new_index = merge_spring.columns.get_loc("iReady_" + term_list[1] +"_stretch_growth") + 1
            merge_spring.insert(new_index, "iReady_" + term_list[1] + '_Lexile', col_to_move)
            col_to_move = merge_spring.pop("iReady_" + term_list[2] + '_Lexile')
            new_index = merge_spring.columns.get_loc("iReady_" + term_list[2] +"_stretch_growth") + 1
            merge_spring.insert(new_index, "iReady_" + term_list[2] + '_Lexile', col_to_move)
        merge_spring.loc[:,"spacer_2"] = "NAN"
        final_merge = merge_spring
    elif len(term_list) == 2:
        #merge winter on all students
        data_list[0] = data_list[0].loc[:,"spacer_0"] = "NAN"
        merge_winter = pd.merge(data_list[0].rename(columns = {"iReady_"+term_list[0]+"_student":"student"}), data_list[1].rename(columns={"iReady_"+term_list[1]+"_student":"student"}), how = "outer", on = "student")
        #feature engineer for whether met growth goals
        merge_winter.loc[merge_winter["iReady_" + term_list[1]+ "_score"]>= merge_winter["iReady_" + term_list[0]+ "_growth_score_goal"], "iReady_" + term_list[1]+ "_typical_growth"] = "YES"
        merge_winter.loc[merge_winter["iReady_" + term_list[1]+ "_score"]< merge_winter["iReady_" + term_list[0]+ "_growth_score_goal"], "iReady_" + term_list[1]+ "_typical_growth"] = "NO"
        merge_winter.loc[merge_winter["iReady_" + term_list[1]+ "_score"]>= merge_winter["iReady_" + term_list[0]+ "_stretch_score_goal"], "iReady_" + term_list[1]+ "_stretch_growth"] = "YES"
        merge_winter.loc[merge_winter["iReady_" + term_list[1]+ "_score"]< merge_winter["iReady_" + term_list[0]+ "_stretch_score_goal"], "iReady_" + term_list[1]+ "_stretch_growth"] = "NO"
        #how much up/down
        merge_winter.loc[:, "iReady_" + term_list[1]+ "_growth_amount"] = merge_winter.loc[:,"iReady_" + term_list[1]+ "_score"] - merge_winter.loc[:,"iReady_" + term_list[0]+ "_score"]
        if subject == "Reading":
            col_to_move = merge_winter.pop("iReady_" + term_list[1] + '_Lexile')
            new_index = merge_winter.columns.get_loc("iReady_" + term_list[1] +"_stretch_growth") + 1
            merge_winter.insert(new_index, "iReady_" + term_list[1] + '_Lexile', col_to_move)
        merge_winter.loc[:,"spacer_1"] = "NAN"
        final_merge = merge_winter
    else:
        final_merge = data_list[0].rename(columns = {"iReady_"+term_list[0]+"_student":"student"})
    #final cleaning/sorting dependent on whether data is one class or whole grade
    if any(final_merge.columns.str.contains("class")): #returns T/F depending on if there is a class column
        final_merge = final_clean_grade(final_merge)
    else:
        final_merge = final_clean_class(final_merge)
    final_merge.columns = final_merge.columns.str.replace("_", " ")
    return final_merge

# final cleaning of student name: sort students alphabetically by last name
# teacher wanted student's number and first and last name together in the first column
def final_clean_class(final_merge):
    final_merge[["last_name", "first_name"]] =  final_merge.loc[:,"student"].str.split(",", expand = True)
    final_merge = final_merge.drop(columns = ["student"])
    final_merge = final_merge.sort_values(by = ["last_name"]).reset_index(drop = True)
    final_merge["student"] = (final_merge.index + 1).astype("str") + ". " + final_merge["first_name"] + " " + final_merge["last_name"]
    final_merge.insert(0,"student", final_merge.pop("student"))
    final_merge = final_merge.drop(columns = ["first_name", "last_name"])
    numeric_col = final_merge.select_dtypes(include='number').columns.to_list()
    final_merge.loc[:, numeric_col] = final_merge.loc[:, numeric_col].round()
    return final_merge

# final cleaning of student name: sort students alphabetically by last name
# this method could be used if teacher has entire grade's data available
def final_clean_grade(final_merge):
    final_merge[["last_name", "first_name"]] =  final_merge.loc[:,"student"].str.split(",", expand = True)
    final_merge = final_merge.drop(columns = ["student"])
    final_merge = final_merge.sort_values(by = ["class", "last_name"]).reset_index(drop = True)
    final_merge["student"] = (final_merge.index + 1).astype("str") + ". " + final_merge["first_name"] + " " + final_merge["last_name"]
    final_merge.insert(0,"student", final_merge.pop("student"))
    final_merge = final_merge.drop(columns = ["first_name", "last_name"])
    numeric_col = final_merge.select_dtypes(include='number').columns.to_list()
    final_merge.loc[:, numeric_col] = final_merge.loc[:, numeric_col].round()
    return final_merge


# Define custom color logic for Excel spreadsheet----------------
# this coloring was specific to teacher's request

#color whether the students' scores went up or down since previous diagnostic
def color_growth_amount(val):
    if val >= 0:
        return 'background-color: #2d7d3a; color: black;'
    elif val<0:
        return 'background-color: #9c0909; color: black;'
    else:
        return 'background-color: #434544; color: #434544;'

# color whether student met their typical and stretch growth goals
def color_growth(val):
    if val == "YES":
        return 'background-color: #2d7d3a; color: black;'
    elif val == "NO":
        return 'background-color: #9c0909; color: black;'
    else:
        return 'background-color: #434544; color: #434544;'

# color the current grade level the student is scoring for each standard tested
# this also colors NA's gray/black. This allows us to visually account for students who may have moved in or out
# during the school year
def color_grade_level(val):
    early_grades = {"Gr K": "#c94d4d", "Gr 1": "#c96969", "Gr 2": "#eb9b9b", "Gr 3":"#faf2b9"}
    four_grade = {"Early 4":"#b4dbb8", "Mid 4":"#7bb582", "Late 4":"#538a5a"}
    high_grades = {"Gr 5":"#aed7fc", "Gr 6":"#83c1f7", "Gr 7":"#377ebd"}
    misc_list = ["S", "NA", "M"]
    if val in early_grades.keys():
        return "background-color:" + early_grades.get(val) + "; color: black;"
    elif val in four_grade.keys():
        return "background-color:" + four_grade.get(val) + "; color: black;"
    elif val in high_grades.keys():
        return "background-color:" + high_grades.get(val) + "; color: black;"
    elif val in misc_list:
        return';'
    else:
        return'background-color: #434544; color: #434544;'
    
def get_colored_spreadsheet(final_merge_data,full_file_path):
    # get the columns needed for each of the previous three functions. Used regex to identity as generally as possible
    amount_col = final_merge_data.columns[final_merge_data.columns.str.contains("amount", flags=re.IGNORECASE, regex = True)]
    growth_col = final_merge_data.columns[final_merge_data.columns.str.contains("stretch|typical",flags=re.IGNORECASE, regex = True)& final_merge_data.columns.str.contains("growth", regex = True)]
    mask = list(final_merge_data.columns.str.contains("student|stretch|typical|growth|score|lexile|percentile",flags=re.IGNORECASE,  regex = True))
    not_mask = [not x for x in mask]
    grades_col = final_merge_data.columns[not_mask]
    # Apply mapping and export
    (final_merge_data.style.map(color_growth_amount, subset=list(amount_col)).map(color_growth, subset=list(growth_col)).map(color_grade_level, subset=list(grades_col)).highlight_null(color = "#434544").format(precision=0).to_excel(full_file_path, engine = "openpyxl", index = False))

# MAIN---------------------------------------------------
def main_clean_engineering(data_list, subject, full_file_path):
    final_merge_data = merge_engineer(data_list, subject)
    get_colored_spreadsheet(final_merge_data, full_file_path)

# Desktop GUI----------

# def run_setup_gui():
#     setup_window = tk.Tk()
#     setup_window.title("ETL Tool Configuration")
#     setup_window.geometry("350x280")
    
#     subject_var = tk.StringVar(value="Math")
#     fall_var = tk.BooleanVar(value=True)
#     winter_var = tk.BooleanVar(value=False)
#     spring_var = tk.BooleanVar(value=False)
    
#     tk.Label(setup_window, text="1. Select Subject", font=("Arial", 11, "bold")).pack(pady=(10, 2))
#     subject_frame = tk.Frame(setup_window)
#     subject_frame.pack()
#     tk.Radiobutton(subject_frame, text="Math", variable=subject_var, value="Math").pack(side="left", padx=15)
#     tk.Radiobutton(subject_frame, text="Reading", variable=subject_var, value="Reading").pack(side="left", padx=15)
    
#     ttk.Separator(setup_window, orient='horizontal').pack(fill='x', padx=20, pady=10)
    
#     tk.Label(setup_window, text="2. Select Terms to Process", font=("Arial", 11, "bold")).pack(pady=(0, 2))
#     tk.Checkbutton(setup_window, text="Fall Scores", variable=fall_var).pack(anchor="w", padx=60, pady=2)
#     tk.Checkbutton(setup_window, text="Winter Scores", variable=winter_var).pack(anchor="w", padx=60, pady=2)
    
#     tk.Checkbutton(setup_window, text="Spring Scores", variable=spring_var).pack(anchor="w", padx=60, pady=2)
    
#     config_results = {"subject": None, "terms": []}
    
#     def on_submit():
#         config_results["subject"] = subject_var.get()
#         if fall_var.get(): config_results["terms"].append("FALL")
#         if winter_var.get(): config_results["terms"].append("WINTER")
#         if spring_var.get(): config_results["terms"].append("SPRING")
#         setup_window.destroy()

#     tk.Button(setup_window, text="Next", command=on_submit, width=10, bg="#2196F3", fg="black").pack(pady=15)
#     setup_window.mainloop()
#     return config_results

def run_setup_gui():
    setup_window = tk.Tk()
    setup_window.title("ETL Tool Configuration")
    setup_window.geometry("450x750")
    
    try:
        setup_window.tk.call('tk', 'scaling', 2.0)
    except:
        pass
    
    subject_var = tk.StringVar(value="Math")
    fall_var = tk.BooleanVar(value=True)
    winter_var = tk.BooleanVar(value=False)
    spring_var = tk.BooleanVar(value=False)
    
    selected_files = {"FALL": None, "WINTER": None, "SPRING": None}
    term_widgets = {}
    
    def browse_file(term):
        """Open file dialog for specific term"""
        subject = subject_var.get()
        file_path = filedialog.askopenfilename(
            title=f"Select {term.capitalize()} {subject} Test Scores CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            selected_files[term] = file_path
            filename = file_path.split('/')[-1]
            term_widgets[term]["label"].config(text=f"✓ {filename}", fg="green")
        else:
            selected_files[term] = None
            term_widgets[term]["label"].config(text="No file selected", fg="gray")
    
    def update_file_section_visibility():
        """Show/hide file selection rows based on checkbox selection"""
        for term, var in [("FALL", fall_var), ("WINTER", winter_var), ("SPRING", spring_var)]:
            if var.get():
                term_widgets[term]["frame"].pack(anchor="w", padx=50, pady=8, fill="x")
            else:
                term_widgets[term]["frame"].pack_forget()
                selected_files[term] = None
    
    # ===== SECTION 1: Subject Selection =====
    tk.Label(setup_window, text="1. Select Subject", font=("Arial", 12, "bold")).pack(pady=(15, 5))
    subject_frame = tk.Frame(setup_window)
    subject_frame.pack(pady=10)
    tk.Radiobutton(subject_frame, text="Math", variable=subject_var, value="Math", font=("Arial", 11)).pack(side="left", padx=20)
    tk.Radiobutton(subject_frame, text="Reading", variable=subject_var, value="Reading", font=("Arial", 11)).pack(side="left", padx=20)
    
    ttk.Separator(setup_window, orient='horizontal').pack(fill='x', padx=30, pady=15)
    
    # ===== SECTION 2: Term Selection =====
    tk.Label(setup_window, text="2. Select Terms to Process", font=("Arial", 12, "bold")).pack(pady=(5, 10))
    tk.Checkbutton(setup_window, text="Fall Scores", variable=fall_var, font=("Arial", 11), command=update_file_section_visibility).pack(anchor="w", padx=80, pady=5)
    tk.Checkbutton(setup_window, text="Winter Scores", variable=winter_var, font=("Arial", 11), command=update_file_section_visibility).pack(anchor="w", padx=80, pady=5)
    tk.Checkbutton(setup_window, text="Spring Scores", variable=spring_var, font=("Arial", 11), command=update_file_section_visibility).pack(anchor="w", padx=80, pady=5)
    
    ttk.Separator(setup_window, orient='horizontal').pack(fill='x', padx=30, pady=15)
    
    # ===== SECTION 3: File Selection =====
    tk.Label(setup_window, text="3. Select Your Files", font=("Arial", 12, "bold")).pack(pady=(5, 10))
    
    files_container = tk.Frame(setup_window)
    files_container.pack(fill="both", expand=True, padx=30, pady=10)
    
    for term in ["FALL", "WINTER", "SPRING"]:
        frame = tk.Frame(files_container, relief="sunken", borderwidth=1, bg="white")
        term_widgets[term] = {"frame": frame}
        
        term_label = tk.Label(frame, text=f"{term.capitalize()}:", font=("Arial", 11, "bold"), width=10, anchor="w", bg="white")
        term_label.pack(side="left", padx=10, pady=8)
        
        browse_btn = tk.Button(frame, text="Browse File", font=("Arial", 10), width=14, 
                              command=lambda t=term: browse_file(t), bg="#4CAF50", fg="white")
        browse_btn.pack(side="left", padx=5)
        
        status_label = tk.Label(frame, text="No file selected", font=("Arial", 9), fg="gray", anchor="w", bg="white")
        status_label.pack(side="left", padx=10, fill="x", expand=True)
        
        term_widgets[term]["label"] = status_label
    
    config_results = {"subject": None, "terms": [], "files": selected_files}
    
    def on_submit():
        selected_terms = []
        if fall_var.get(): 
            selected_terms.append("FALL")
        if winter_var.get(): 
            selected_terms.append("WINTER")
        if spring_var.get(): 
            selected_terms.append("SPRING")
        
        missing_files = [term for term in selected_terms if not selected_files[term]]
        
        if missing_files:
            messagebox.showwarning("Missing Files", f"Please select files for: {', '.join(missing_files)}")
            return
        
        config_results["subject"] = subject_var.get()
        config_results["terms"] = selected_terms
        setup_window.destroy()

    tk.Button(setup_window, text="Next", command=on_submit, width=12, font=("Arial", 11, "bold"), bg="#2196F3", fg="white").pack(pady=20)
    
    update_file_section_visibility()
    setup_window.mainloop()
    return config_results

# if __name__ == "__main__":
#     user_config = run_setup_gui()

#     if not user_config["subject"] or not user_config["terms"]:
#         root = tk.Tk()
#         root.withdraw()
#         messagebox.showwarning("Cancelled", "Configuration incomplete. Exiting tool.")
#         root.destroy()
#         exit()

#     chosen_subject = user_config["subject"]
#     terms_to_prompt = user_config["terms"]
    
#     root = tk.Tk()
#     root.withdraw()
    
#     try:
#         # Use selected files directly instead of opening dialogs
#         csv_dataframes_list = [pd.read_csv(user_config["files"][term]) for term in terms_to_prompt]
        
#         output_path = filedialog.asksaveasfilename(
#             title=f"Save Final {chosen_subject} Score Report",
#             defaultextension=".xlsx",
#             filetypes=[("Excel files", "*.xlsx")]
#         )
        
#         if output_path:
#             main_clean_engineering(csv_dataframes_list, chosen_subject, output_path)
#             messagebox.showinfo("Success", f"{chosen_subject} data ETL complete! Excel sheet created successfully.")
#         else:
#             messagebox.showwarning("Cancelled", "Export cancelled. File was not saved.")
            
#     except Exception as e:
#         messagebox.showerror("Error", f"An error occurred during processing:\n{str(e)}")
        
#     root.destroy()

if __name__ == "__main__":
    user_config = run_setup_gui()

    if not user_config["subject"] or not user_config["terms"]:
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning("Cancelled", "Configuration incomplete. Exiting tool.")
        root.destroy()
        exit()

    chosen_subject = user_config["subject"]
    terms_selected = user_config["terms"]
    
    root = tk.Tk()
    root.withdraw()
    
    try:
        # Create dictionary mapping term names to dataframes
        csv_dataframes_dict = {}
        for term in terms_selected:
            # Map full term names to abbreviations for dictionary keys
            term_abbrev = term[:2].lower()  # "FALL" -> "fa", "WINTER" -> "wi", "SPRING" -> "sp"
            file_path = user_config["files"][term]
            csv_dataframes_dict[term_abbrev] = pd.read_csv(file_path)
        
        output_path = filedialog.asksaveasfilename(
            title=f"Save Final {chosen_subject} Score Report",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        
        if output_path:
            main_clean_engineering(csv_dataframes_dict, chosen_subject, output_path)
            messagebox.showinfo("Success", f"{chosen_subject} data ETL complete! Excel sheet created successfully.")
        else:
            messagebox.showwarning("Cancelled", "Export cancelled. File was not saved.")
            
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during processing:\n{str(e)}")
        
    root.destroy()




