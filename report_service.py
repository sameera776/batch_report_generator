import pandas as pd
import os
import json

class ReportService:

    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path

    def load_data(self):
        try:
            self.students = pd.read_csv(os.path.join(self.input_path, "students.csv"))
            self.attendance = pd.read_csv(os.path.join(self.input_path, "attendance.csv"))
            self.marks = pd.read_csv(os.path.join(self.input_path, "marks.csv"))
        except FileNotFoundError as e:
            print("❌ Error: One or more input files are missing.")
            raise SystemExit(e)

    def clean_data(self):
        # Remove duplicates
        self.students.drop_duplicates(inplace=True)
        self.attendance.drop_duplicates(inplace=True)
        self.marks.drop_duplicates(inplace=True)

        # Handle missing values
        self.students.fillna("", inplace=True)
        self.attendance.fillna(0, inplace=True)
        self.marks.fillna(0, inplace=True)

        # Convert types
        self.attendance["totalClasses"] = pd.to_numeric(self.attendance["totalClasses"])
        self.attendance["attendedClasses"] = pd.to_numeric(self.attendance["attendedClasses"])
        self.marks["marks"] = pd.to_numeric(self.marks["marks"])

    def generate_report(self):
        # Attendance %
        self.attendance["attendancePercent"] = (
            self.attendance["attendedClasses"] / self.attendance["totalClasses"] * 100
        )

        # Average marks per student
        avg_marks = self.marks.groupby("studentId")["marks"].mean().reset_index()
        avg_marks.rename(columns={"marks": "avgMarks"}, inplace=True)

        # Merge all
        report = self.students.merge(self.attendance, on="studentId")
        report = report.merge(avg_marks, on="studentId")

        # Status
        report["status"] = report["avgMarks"].apply(
            lambda x: "PASS" if x >= 40 else "FAIL"
        )

        final_report = report[
            ["studentId", "name", "attendancePercent", "avgMarks", "status"]
        ]

        final_report.to_csv(os.path.join(self.output_path, "report.csv"), index=False)

        return final_report

    def generate_summary(self, report):
        summary = {
            "totalStudents": len(report),
            "avgAttendance": report["attendancePercent"].mean(),
            "avgMarks": report["avgMarks"].mean(),
            "passCount": len(report[report["status"] == "PASS"]),
            "failCount": len(report[report["status"] == "FAIL"]),
            "top3Students": report.sort_values(by="avgMarks", ascending=False)
                                .head(3)["name"].tolist()
        }

        with open(os.path.join(self.output_path, "summary.json"), "w") as f:
            json.dump(summary, f, indent=4)