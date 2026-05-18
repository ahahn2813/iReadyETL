import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re
import openpyxl
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

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

def clean_iready_math(iready_math, term):
    iready_math.columns = iready_math.columns.str.lower().str.replace(" ", "_")
    drop_list = list(iready_math.columns[iready_math.columns.str.contains("relative|quantile|projection|proficiency|date|flag|language", regex = True)])
    #drop_list = drop_rel_list + ["projection_if_student_achieves_typical_growth", "projection_if_student_achieves_stretch_growth", "proficiency_if_student_shows_no_additional_growth", "diagnostic_language", "date", "rush_flag"]
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


def merge_engineer(data_list, subject):
    if len(data_list) == 3:
        term_list = ["FA", "WI", "SP"]
    elif len(data_list) == 2:
        term_list = ["FA", "WI"]
    else:
        term_list = ["FA"]
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


# Define custom color logic
def color_growth_amount(val):
    if val >= 0:
        return 'background-color: #2d7d3a; color: black;'
    elif val<0:
        return 'background-color: #9c0909; color: black;'
    else:
        return 'background-color: #434544; color: #434544;'
    
def color_growth(val):
    if val == "YES":
        return 'background-color: #2d7d3a; color: black;'
    elif val == "NO":
        return 'background-color: #9c0909; color: black;'
    else:
        return 'background-color: #434544; color: #434544;'
    
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
    # Apply mapping and export
    amount_col = final_merge_data.columns[final_merge_data.columns.str.contains("amount", flags=re.IGNORECASE, regex = True)]
    growth_col = final_merge_data.columns[final_merge_data.columns.str.contains("stretch|typical",flags=re.IGNORECASE, regex = True)& final_merge_data.columns.str.contains("growth", regex = True)]
    mask = list(final_merge_data.columns.str.contains("student|stretch|typical|growth|score|lexile|percentile",flags=re.IGNORECASE,  regex = True))
    not_mask = [not x for x in mask]
    grades_col = final_merge_data.columns[not_mask]
    (final_merge_data.style.map(color_growth_amount, subset=list(amount_col)).map(color_growth, subset=list(growth_col)).map(color_grade_level, subset=list(grades_col)).highlight_null(color = "#434544").format(precision=0).to_excel(full_file_path, engine = "openpyxl", index = False))

def main_clean_engineering(data_list, subject, full_file_path):
    # FIXED: Adjusted pipeline parameters to accept target destination directory dynamically
    final_merge_data = merge_engineer(data_list, subject)
    get_colored_spreadsheet(final_merge_data, full_file_path)

# --- RUNTIME RUN DESKTOP GUI ---

def run_setup_gui():
    setup_window = tk.Tk()
    setup_window.title("ETL Tool Configuration")
    setup_window.geometry("350x280")
    
    subject_var = tk.StringVar(value="Math")
    fall_var = tk.BooleanVar(value=True)
    winter_var = tk.BooleanVar(value=False)
    spring_var = tk.BooleanVar(value=False)
    
    tk.Label(setup_window, text="1. Select Subject", font=("Arial", 11, "bold")).pack(pady=(10, 2))
    subject_frame = tk.Frame(setup_window)
    subject_frame.pack()
    tk.Radiobutton(subject_frame, text="Math", variable=subject_var, value="Math").pack(side="left", padx=15)
    tk.Radiobutton(subject_frame, text="Reading", variable=subject_var, value="Reading").pack(side="left", padx=15)
    
    ttk.Separator(setup_window, orient='horizontal').pack(fill='x', padx=20, pady=10)
    
    tk.Label(setup_window, text="2. Select Terms to Process", font=("Arial", 11, "bold")).pack(pady=(0, 2))
    tk.Checkbutton(setup_window, text="Fall Scores", variable=fall_var).pack(anchor="w", padx=60, pady=2)
    tk.Checkbutton(setup_window, text="Winter Scores", variable=winter_var).pack(anchor="w", padx=60, pady=2)
    
    # FIXED: Changed from 'selection_window' back to tracking scope target 'setup_window'
    tk.Checkbutton(setup_window, text="Spring Scores", variable=spring_var).pack(anchor="w", padx=60, pady=2)
    
    config_results = {"subject": None, "terms": []}
    
    def on_submit():
        config_results["subject"] = subject_var.get()
        if fall_var.get(): config_results["terms"].append("FALL")
        if winter_var.get(): config_results["terms"].append("WINTER")
        if spring_var.get(): config_results["terms"].append("SPRING")
        setup_window.destroy()

    tk.Button(setup_window, text="Next", command=on_submit, width=10, bg="#2196F3", fg="black").pack(pady=15)
    setup_window.mainloop()
    return config_results

if __name__ == "__main__":
    user_config = run_setup_gui()

    if not user_config["subject"] or not user_config["terms"]:
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning("Cancelled", "Configuration incomplete. Exiting tool.")
        root.destroy()
        exit()

    chosen_subject = user_config["subject"]
    terms_to_prompt = user_config["terms"]

    root = tk.Tk()
    root.withdraw()
    csv_dataframes_list = []
    
    try:
        for term in terms_to_prompt:
            title_text = f"Select {term} {chosen_subject.upper()} Test Scores CSV"
            path = filedialog.askopenfilename(title=title_text, filetypes=[("CSV files", "*.csv")])
            
            if path:
                df = pd.read_csv(path)
                csv_dataframes_list.append(df)
            else:
                messagebox.showwarning("Cancelled", f"You did not select a file for {term}. Process cancelled.")
                root.destroy()
                exit()
            
        output_path = filedialog.asksaveasfilename(
            title=f"Save Final {chosen_subject} Score Report",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        
        if output_path:
            main_clean_engineering(csv_dataframes_list, chosen_subject, output_path)
            messagebox.showinfo("Success", f"{chosen_subject} data ETL complete! Excel sheet created successfully.")
        else:
            messagebox.showwarning("Cancelled", "Export cancelled. File was not saved.")
            
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during processing:\n{str(e)}")
        
    root.destroy()




