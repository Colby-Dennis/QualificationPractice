import tkinter as tk
from PIL import ImageTk, Image
import pandas as pd

'''
TO DO LIST:
    4.) METHOD TO SHOW QUESTION ON SCREEN
    5.) METHOD TO REVEAL THE SKILLS THAT QUESTION USES.
    6.) SAVE USER RESPONSE ON THEIR EXECUTION OF THAT SKILL.
    7.) METHOD TO CHANGE QUESTION TYPES
'''

# CLASSES FOR THE OBJECTS
# Pass in the df row using df.iloc[#]
class Skill:
    def __init__(self, dataFrameRow):
        self.skillID = dataFrameRow["Skill ID"]
        self.subjectCategory = dataFrameRow["Subject Category ID"]
        self.skillName = dataFrameRow["Skill Name"]
        self.skillDescription = dataFrameRow["Skill Description"]
        self.skillQuestions = convertToIntArray(dataFrameRow["Question List"])
        self.skillAttempts = convertToIntArray(dataFrameRow["Skill Attempts"])
        self.skillMastery = dataFrameRow["Skill Mastery"]


class Question:
    def __init__(self, dataFrameRow):
        self.questionID = dataFrameRow["Question ID"]
        self.subjectCategory = dataFrameRow["Subject Category ID"]
        self.questionImageLink = dataFrameRow["Question Image Link"]
        self.questionAnswerLink = dataFrameRow["Question Answer Link"]
        self.questionSource = dataFrameRow["Question Source"]
        self.questionSkills = convertToIntArray(dataFrameRow["Skills String"])
        
class Subject:
    def __init__(self, dataFrameRow):
        self.subjectID = dataFrameRow["Subject ID"]
        self.subjectName = dataFrameRow["Subject Name"]
        self.subjectDescription = dataFrameRow["Subject Description"]

# USEFUL FUNCTIONS
def convertToIntArray(string):
    if (not(type(string) is str)):
        return [string]
    else:
        tempString = string.split(";")
        tempInt = []
        for val in tempString:
            tempInt.append(int(val))
        return tempInt
    
def convertToStorageString(array):
    if len(array) == 0:
        return ""
    else:
        string = ""
        for val in array:
            string = string + ";" + str(val)
        string = string[1:]
        return string
    
def calculateMastery(array):
    total = 0
    if len(array) >= 10:
        for i in range(1,11):
            total = total + (array[len(array)-i] * 5)
    else:
        for value in array:
            total = total + (value * 5)
    return total

# A function that updates what questions are tied to a specific skill
def updateQuestionList(questionDataBase, skillDataBase):
    # Need to loop through each skill and update question list
    for skill in skillDataBase.iloc:
        questionList = []
        for question in questionDataBase.iloc:
            if skill["Skill ID"] in convertToIntArray(question["Skills String"]):
                questionList.append(question["Question ID"])
        skillDataBase.at[skill["Skill ID"], "Question List"] = convertToStorageString(questionList)
    skillDataBase.to_excel("Databases/SkillsDB.xlsx", index=False)
    
    
def getQuestionBank(subjectID, skillDatabase, questionDatabase):
    tempSkillDatabase = skillDatabase.loc[skillDatabase["Subject Category ID"] == subjectID]
    tempSkillDatabase = tempSkillDatabase.sort_values(by="Skill Mastery")
    questionBank = pd.DataFrame(columns = list(questionDatabase.columns))
    # Populating the question bank
    for row in tempSkillDatabase.iloc:
        questionList = convertToIntArray(row["Question List"])
        for q in questionList:
            if not(q in questionBank["Question ID"]):
                #print(questionDatabase.loc[questionDatabase['Question ID'] == q])
                #questionBank = questionBank.append(questionDatabase.loc[questionDatabase['Question ID'] == q])
                questionBank = pd.concat([questionBank,questionDatabase.loc[questionDatabase['Question ID'] == q]])
    return(questionBank)
    
def startQuestionAttempts(controller, subjectID, questionBank, skillDatabase, questionDatabase):
    questionBank = getQuestionBank(subjectID, skillDatabase, questionDatabase)
    controller.loadNextQuestion(questionBank);
    controller.show_frame("QuestionPage")
    

# GETTING THE DATABASES
subjectDB = pd.read_excel('Databases/SubjectCategory.xlsx')
questionDB = pd.read_excel('Databases/QuestionDB.xlsx')
skillDB = pd.read_excel('Databases/SkillsDB.xlsx')

# Essential updates as needed.
updateQuestionList(questionDB, skillDB)

class StudyApp:
    def __init__(self, skillDataBase, questionDataBase):
        self.root = tk.Tk()
        self.root.title("Prelim Practice")
        self.root.iconbitmap("atom.ico")
        self.questionPath = "default.png"
        self.answerPath = "default.png"
        self.pageLabel = "Select Subject"
        self.imageX = 500
        self.imageY = 500
        self.root.pageLabel = tk.Label(text=self.pageLabel)
        self.root.buttons = []
        self.root.labels = []
        self.skillDB = skillDataBase
        self.questionDB = questionDataBase
        self.questionBank = pd.DataFrame(columns = list(self.questionDB.columns))
        self.questionImageInfo = ImageTk.PhotoImage(self.getScaledImage(self.questionPath))
        self.answerImageInfo = ImageTk.PhotoImage(self.getScaledImage(self.answerPath))
        self.root.questionImage = tk.Label(image=self.questionImageInfo)
        self.root.answerImage = tk.Label(image=self.answerImageInfo)
        self.currentSkills = []
        self.root.skillsRadioButtons = []
        self.skillMastery = []
        self.showSubjectSelect()
        
    def showSubjectSelect(self):
        self.clearPage()
        self.pageLabel = "Select Subject"
        self.root.pageLabel.config(text=self.pageLabel)
        self.root.buttons.append(tk.Button(text="Mathematics", command=lambda: 
                                         self.loadQuestions(0, self.skillDB, self.questionDB)))
        self.root.buttons.append(tk.Button(text="Classical Mechanics", command=lambda: 
                                         self.loadQuestions(1, self.skillDB, self.questionDB)))
        self.root.buttons.append(tk.Button(text="Quantum Mechanics", command=lambda: 
                                         self.loadQuestions(2, self.skillDB, self.questionDB)))
        self.root.buttons.append(tk.Button(text="Electrodynamics", command=lambda: 
                                         self.loadQuestions(3, self.skillDB, self.questionDB)))
        self.root.buttons.append(tk.Button(text="Statistical Mechanics", command=lambda: 
                                         self.loadQuestions(4, self.skillDB, self.questionDB)))
            
        self.root.pageLabel.grid(row=0, column=0, columnspan=5)
        i = 0
        for btn in self.root.buttons:
            btn.grid(row=1, column=i)
            i = i + 1

    def loadQuestions(self, subjectID, skillDataBase, questionDataBase):
        self.questionBank = getQuestionBank(subjectID, skillDataBase, questionDataBase)
        self.loadNextQuestionInfo()
        
        
    def show(self):
        self.root.mainloop()
        
    def loadNextQuestionInfo(self):
        # PROCESS SKILLS IF THEY EXIST
        if len(self.root.skillsRadioButtons) > 0:
            # Processing results
            for i in range(len(self.currentSkills)):
                # Updating skill attempts
                skillAttempts = convertToIntArray(self.skillDB.iloc[
                    self.currentSkills[i]]["Skill Attempts"])
                skillAttempts.append(self.skillMastery[i].get())
                # updating mastery
                self.skillDB.at[self.currentSkills[i],"Skill Attempts"
                                ]=convertToStorageString(skillAttempts)
                self.skillDB.at[self.currentSkills[i],"Skill Mastery"
                                ]=calculateMastery(skillAttempts)
            # Updating the database
            self.skillDB.to_excel("Databases/SkillsDB.xlsx", index=False)

        if self.questionBank.shape[0] > 0:
            # updating necessary information
            self.questionPath = self.questionBank.iloc[0]["Question Image Link"]
            self.answerPath = self.questionBank.iloc[0]["Question Answer Link"]
            self.currentSkills = convertToIntArray(self.questionBank.iloc[0]["Skills String"])
            self.pageLabel = self.questionBank.iloc[0]["Question Source"]
            self.root.pageLabel.config(text=self.pageLabel)
            self.questionBank = self.questionBank[1:]
            self.showQuestion()
            self.root.buttons.append(tk.Button(text="Show Answer", command=lambda:
                                                   self.showAnswer()))
            
            for btn in self.root.buttons:
                btn.grid(row=3, column=0, columnspan=5);
        else :
            self.showSubjectSelect()
            
    def showQuestion(self):
        self.clearPage()
        self.questionImageInfo = ImageTk.PhotoImage(self.getScaledImage(self.questionPath))
        self.root.questionImage = tk.Label(image=self.questionImageInfo)
        self.root.questionImage.grid(row=2, column=0, columnspan=5)
        
    def showAnswer(self):
        self.clearPage()
        self.answerImageInfo = ImageTk.PhotoImage(self.getScaledImage(self.answerPath))
        self.root.answerImage = tk.Label(image=self.answerImageInfo)
        self.root.answerImage.grid(row=1, column=0, columnspan=5)
        self.root.buttons.append(tk.Button(text="Next Question", command=lambda:
                                  self.loadNextQuestionInfo()))
        
        for btn in self.root.buttons:
            btn.grid(row=2, column=0, columnspan=5)
            
        # adding mastery labels
        i = 0
        labels=["Skill Name", "Applied Incorrectly", "Correct w/ Resources",
                "Correct w/o Resources"]
        for lab in labels:
            self.root.labels.append(tk.Label(text=lab,
                                             padx=10,
                                             pady=30))
            i = i + 1
        i=0
        for lbl in self.root.labels:
            lbl.grid(row=3, column=i)
            i = i + 1
        
        i = 4
        self.skillMastery = []
        # Adding the radio buttons
        for skill in self.currentSkills:
            self.skillMastery.append(tk.IntVar())
            self.skillMastery[len(self.skillMastery)-1].set(0)
            skillName = self.skillDB.iloc[skill]["Skill Name"]
            self.root.labels.append(tk.Label(
                text=skillName, padx=10))
            self.root.labels[len(self.root.labels)-1].grid(row=i, column=0)
            # incorrect button
            self.root.skillsRadioButtons.append(tk.Radiobutton(
                variable = self.skillMastery[i-4],
                value=0))
            self.root.skillsRadioButtons[len(self.root.skillsRadioButtons)-1].grid(row=i, column=1)
            # correct with resource button
            self.root.skillsRadioButtons.append(tk.Radiobutton(
                variable = self.skillMastery[i-4],
                value=1))
            self.root.skillsRadioButtons[len(self.root.skillsRadioButtons)-1].grid(row=i, column=2)
            # correct button
            self.root.skillsRadioButtons.append(tk.Radiobutton(
                variable = self.skillMastery[i-4],
                value=2))
            self.root.skillsRadioButtons[len(self.root.skillsRadioButtons)-1].grid(row=i, column=3)
            i = i + 1
    
    def getScaledImage(self, imagePath):
        image = Image.open(imagePath)
        oldX = image.size[0]
        oldY = image.size[1]
        scale = 1
        if oldX>oldY:
                scale = 500/oldX
        else:
            scale = 500/oldY
        if scale > 1:
            scale = 1
        
        image = image.resize((int(oldX*scale), int(oldY*scale)))
        return image
    
    def clearPage(self):
        if self.root.questionImage:
            self.root.questionImage.destroy()
        if self.root.answerImage:
            self.root.answerImage.destroy()
        for btn in self.root.buttons:
            btn.destroy()
        self.root.buttons = []
        for lbl in self.root.labels:
            lbl.destroy()
        self.root.labels = []
        for btn in self.root.skillsRadioButtons:
            btn.destroy()
        self.root.skillsRadioButtons = []

        

# Trying a more basic Tkinter window viewer
app = StudyApp(skillDB, questionDB)
app.show()

# NOTE: myCanvas.delete('all') will clear everything in the canvas!!!!

