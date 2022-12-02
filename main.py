# loading csv
import pandas as pd
from pathlib import Path
import numpy as np
import matplotlib.pyplot as mp

data = Path(__file__).parent/"data"

roster = pd.read_csv(
    data / "roster.csv",
    converters={"NetID": str.lower, "Email Address": str.lower},
    usecols=["NetID", "Email Address", "Section"],
    index_col= "NetID"
)

homework = pd.read_csv(
    data / "hw_exam_grades.csv",
    converters={"SID": str.lower},
    usecols=lambda x: "Submission" not in x,
    index_col= "SID"
)



quiz_grades = pd.DataFrame()

for file in data.glob("quiz_*_grades.csv"):
    quiz_name = " ".join(file.stem.title().split("_")[:2])
    quiz = pd.read_csv(
        file,
        usecols = ["Email", "Grade"],
        index_col = "Email"
    ).rename(columns={"Grade" : quiz_name})
    quiz_grades = pd.concat([quiz_grades, quiz], axis = 1)

# print(quiz_grades.head())

final_data = pd.merge(
    roster,
    homework,
    left_index=True,
    right_index=True,
)

final_data = pd.merge(
    final_data,
    quiz_grades,
    left_on =  "Email Address",
    right_index = True
)


for x in range(1,4):
    final_data[f"Exam {x} score"] = final_data[f"Exam {x}"] / final_data[f"Exam {x} - Max Points"]


hw_scores = final_data.filter(regex=r"^Homework \d\d?$",axis = 1)
hw_max_scores = final_data.filter(regex=r"^Homework \d\d? - ",axis = 1)
hw_scores = hw_scores.sum(axis = 1)
hw_max_scores = hw_max_scores.sum(axis = 1)
avg_hw = hw_scores/hw_max_scores
# print(avg_hw)

final_data["Average Homework"] = avg_hw
#print(final_data)

quiz_scores = final_data.filter(regex=r"^Quiz \d\d?$",axis = 1)
quiz_scores = quiz_scores.sum(axis = 1)
avg_quiz = quiz_scores/100
final_data["Average Quiz"] = avg_quiz
# print(avg_quiz)

weightings = pd.Series(
    {
        "Exam 1 score": 0.1,
        "Exam 2 score": 0.15,
        "Exam 3 score": 0.2,
        "Average Quiz": 0.3,
        "Average Homework": 0.25,

    }
)

final_data["Final Score"] = (final_data[weightings.index] * weightings).sum(axis = 1)
final_data["Ceiling Score"] = np.ceil(final_data["Final Score"] * 100)

grades = {
    90 : 'A',
    75 : 'B',
    65 : 'C',
    50 : 'D',
    0 : 'F'
}
def grade_mapping(grade_val):
    for key,value in grades.items():
            if grade_val >= key:
                return value

plotting = final_data["Ceiling Score"].map(grade_mapping)


final_data["Final Grade"] = plotting

final_data["Final Score"].plot.hist(bins = 25, label = "Histogram Graph")
final_data["Final Score"].plot.density(linewidth = 4, label = "Density Estimate Graph")
mp.show()

#print(grade_mapping())

# print(final_data["Exam 1 score"])
 
# a = lambda x,y: x+y

# file = data / "quiz_4_grades.csv"

# print(" ".join(file.stem.title().split("_")[:2]))


#print(final_data.head())