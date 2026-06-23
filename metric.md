# 选择的指标 20个
## 1
    {
        "calculator id": 2,
        "calculator name": "Creatinine Clearance (Cockcroft-Gault Equation)",
        "category": "lab",
        "output type": "decimal",
        "question": "What is the patient's Creatinine Clearance using the Cockroft-Gault Equation in terms of mL/min? You should use the patient's adjusted body weight in kg instead of the patient's actual body weight if the patient is overweight or obese based on their BMI. If the patient's BMI's normal, set their adjusted body weight to the minimum of the ideal body and actual weight. If the patient is underweight, please set their adjusted body weight to their actual body weight.",
        "formula": "The formula for computing Creatinine Clearance (CrCl) using the Cockcroft-Gault Equation is:\nCrCl (mL/min) = ((140 - age) x weight x gender_coefficient) / (72 x serum creatinine in mg/dL),\nwhere gender_coefficient = 1 if male, 0.85 if female, and the weight used depends on BMI as follows: if BMI < 18.5 (underweight), use actual body weight; if BMI is between 18.5 and 24.9 (normal weight), use ideal body weight (IBW); if BMI ≥ 25 (overweight/obese), use adjusted body weight (ABW).\nThe formula for computing the patient's body mass index (BMI) is (weight)/(height * height), where weight is the patient's weight in kg and height is the patient's height in m.\nIdeal body weight is calculated using the Devine formula:\nIBW (kg) = 50 + 2.3 x (height in inches - 60) for males,\nIBW (kg) = 45.5 + 2.3 x (height in inches - 60) for females.\nAdjusted body weight is calculated as: ABW (kg) = IBW + 0.4 x (actual body weight - IBW).",
        "example": "Patient: 65-year-old male, weight 85 kg, height 1.70 m, serum creatinine 1.2 mg/dL.\nStep 1 - Calculate BMI: 85 / (1.70 * 1.70) = 29.4 kg/m² (overweight, use ABW).\nStep 2 - Calculate IBW: 50 + 2.3 * ((1.70/0.0254) - 60) = 50 + 2.3 * (66.9 - 60) = 50 + 15.9 = 65.9 kg.\nStep 3 - Calculate ABW: 65.9 + 0.4 * (85 - 65.9) = 65.9 + 7.6 = 73.5 kg.\nStep 4 - CrCl = ((140 - 65) * 73.5 * 1) / (72 * 1.2) = (75 * 73.5) / 86.4 = 5512.5 / 86.4 = 63.8 mL/min."
    },

## 2
    {
        "calculator id": 3,
        "calculator name": "CKD-EPI Equations for Glomerular Filtration Rate",
        "category": "lab",
        "output type": "decimal",
        "question": "Using the 2021 CKD-EPI Creatinine equation, what is the patient's Glomerular Filtration Rate (GFR) in terms of mL/min/1.73 m²?",
        "formula": "Using the 2021 CKD-EPI Creatinine equation, patient's Glomerular Filtration Rate (GFR) can be computed as 142 x (Scr/A)^B x 0.9938^age x gender_coefficient, where the ^ indicates an exponent operation, Scr is the concentration of serum creatinine in mg/dL, and gender_coefficient is 1.012 if the patient is female, else the coefficient is 1. The coefficients A and B are determined based on gender and Scr: for females, A = 0.7 and B = -0.241 if Scr ≤ 0.7, A = 0.7 and B = -1.2 if Scr > 0.7; for males, A = 0.9 and B = -0.302 if Scr ≤ 0.9, A = 0.9 and B = -1.2 if Scr > 0.9.",
        "example": "Patient: 50-year-old female, serum creatinine 0.6 mg/dL.\nStep 1 - For female, A = 0.7. Since Scr 0.6 ≤ 0.7, B = -0.241. gender_coefficient = 1.012.\nStep 2 - GFR = 142 * (0.6/0.7)^(-0.241) * 0.9938^50 * 1.012\nStep 3 - (0.6/0.7)^(-0.241) = (0.857)^(-0.241) = 1.037\nStep 4 - 0.9938^50 = 0.731\nStep 5 - GFR = 142 * 1.037 * 0.731 * 1.012 = 142 * 0.767 = 108.9 mL/min/1.73 m²."
    },

## 3
    {
        "calculator id": 4,
        "calculator name": "CHA2DS2-VASc Score for Atrial Fibrillation Stroke Risk",
        "category": "risk",
        "output type": "integer",
        "question": "What is the patient's CHA2DS2-VASc Score?",
        "formula": "The criteria for the CHA2DS2-VASc score are listed below:\n\n1. Age: < 65 years = 0 points, 65-74 years = +1 point, ≥ 75 years = +2 points\n2. Sex: Female = +1 point, Male = 0 points\n3. Congestive Heart Failure (CHF) history: No = 0 points, Yes = +1 point\n4. Hypertension history: No = 0 points, Yes = +1 point\n5. Stroke, Transient Ischemic Attack (TIA), or Thromboembolism history: No = 0 points, Yes = +2 points\n6. Vascular disease history (previous myocardial infarction, peripheral artery disease, or aortic plaque): No = 0 points, Yes = +1 point\n7. Diabetes history: No = 0 points, Yes = +1 point\n\nThe CHA2DS2-VASc score is calculated by summing the points for each criterion.",
        "example": "Patient: 72-year-old male with hypertension and diabetes, no stroke, no CHF, no vascular disease.\nStep 1 - Age 72 (≥75? No, 65-74? Yes): +1 point.\nStep 2 - Sex male: 0 points.\nStep 3 - Hypertension: Yes = +1 point.\nStep 4 - Diabetes: Yes = +1 point.\nStep 5 - Stroke: No = 0 points. CHF: No = 0 points. Vascular disease: No = 0 points.\nTotal CHA2DS2-VASc Score = 1 + 0 + 1 + 1 = 3."
    },

## 4
    {
        "calculator id": 5,
        "calculator name": "Mean Arterial Pressure (MAP)",
        "category": "physical",
        "output type": "decimal",
        "question": "What is patient's mean arterial pressure in mm Hg?",
        "formula": "The mean arterial pressure is computed by the formula 1/3 * (systolic blood pressure) + 2/3 * (diastolic blood pressure)",
        "example": "Patient: systolic BP 120 mmHg, diastolic BP 80 mmHg.\nMAP = (1/3 * 120) + (2/3 * 80) = 40 + 53.3 = 93.3 mm Hg."
    },

## 5
    {
        "calculator id": 6,
        "calculator name": "Body Mass Index (BMI)",
        "category": "physical",
        "output type": "decimal",
        "question": "What is the patient's body mass mass index (BMI)? Your answer should be in terms of kg/m².",
        "formula": "The formula for computing the patient's body mass index (BMI) is (weight)/(height * height), where weight is the patient's weight in kg and height is the patient's height in m.",
        "example": "Patient: weight 78 kg, height 1.75 m.\nBMI = 78 / (1.75 * 1.75) = 78 / 3.0625 = 25.5 kg/m²."
    },

## 6
    {
        "calculator id": 9,
        "calculator name": "MDRD GFR Equation",
        "category": "lab",
        "output type": "decimal",
        "question": "Using the MDRD GFR equation, what is the patient's Glomerular Filtration Rate (GFR) in terms of mL/min/1.73 m²?",
        "formula": "The patient's estimated GFR is calculated using the MDRD equation as:\nGFR = 175 * creatinine^(-1.154) * age^(-0.203) * race_coefficient(=1.0 if race is non-Black or unspecified; =1.212 if African American; ) * gender_coefficient(0.742 if female, 1 if male). The creatinine concentration is mg/dL. Note: If race is NOT mentioned, use 1.0 as the race coefficient.",
        "example": "Patient: 55-year-old African-American male, serum creatinine 1.5 mg/dL.\nStep 1 - race_coefficient = 1.212, gender_coefficient = 1.\nStep 2 - creatinine^(-1.154) = 1.5^(-1.154) = 0.630\nStep 3 - age^(-0.203) = 55^(-0.203) = 0.443\nStep 4 - GFR = 175 * 0.630 * 0.443 * 1.212 * 1 = 175 * 0.338 = 59.2 mL/min/1.73 m²."
    },

## 7
    {
        "calculator id": 10,
        "calculator name": "Ideal Body Weight",
        "category": "physical",
        "output type": "decimal",
        "question": "Using the Ideal Body Weight Formula, what is the patient's ideal body weight in terms of kg?",
        "formula": "Using the Ideal Body Weight Formula to calculate IBW: For males, the patient's ideal body weight (IBW) is calculated as follows:\nIBW = 50 kg + 2.3 kg * (height (in inches) - 60). \n For females, the ideal body weight (IBW) is calculated as follows:\nIBW = 45.5 kg + 2.3 kg * (height (in inches) - 60).",
        "example": "Patient: 30-year-old female, height 5 ft 5 in (65 inches).\nIBW = 45.5 + 2.3 * (65 - 60) = 45.5 + 2.3 * 5 = 45.5 + 11.5 = 57.0 kg."
    },
## 8
    {
        "calculator id": 11,
        "calculator name": "QTc Bazett Calculator",
        "category": "physical",
        "output type": "decimal",
        "question": "Using the Bazett Formula for corrected QT interval, what is the patient's corrected QT interval in msec?",
        "formula": "The corrected QT interval using the Bazett formula is computed as QTc = QT interval (msec) / √(RR interval (sec)), where the QT interval is measured in milliseconds (msec), and the RR interval is given as 60 ÷ heart rate (beats/min), resulting in RR interval in seconds (sec).",
        "example": "Patient: QT interval 420 msec, heart rate 75 bpm.\nStep 1 - RR interval = 60 / 75 = 0.8 sec.\nStep 2 - QTc = 420 / sqrt(0.8) = 420 / 0.894 = 469.6 msec."
    },

## 9
    {
        "calculator id": 15,
        "calculator name": "Child-Pugh Score for Cirrhosis Mortality",
        "category": "severity",
        "output type": "integer",
        "question": "What is the patient's Child-Pugh Score?",
        "formula": "The criteria for the Child-Pugh Score are listed below:\n\n1. Bilirubin (Total): <2 mg/dL (<34.2 μmol/L) = +1 point, 2-3 mg/dL (34.2-51.3 μmol/L) = +2 points, >3 mg/dL (>51.3 μmol/L) = +3 points\n2. Albumin: >3.5 g/dL (>35 g/L) = +1 point, 2.8-3.5 g/dL (28-35 g/L) = +2 points, <2.8 g/dL (<28 g/L) = +3 points\n3. INR: <1.7 = +1 point, 1.7-2.3 = +2 points, >2.3 = +3 points\n4. Ascites: Absent = +1 point, Slight = +2 points, Moderate = +3 points\n5. Encephalopathy: No Encephalopathy = +1 point, Grade 1-2 = +2 points, Grade 3-4 = +3 points \n(Grade 0: normal consciousness, personality, neurological examination, electroencephalogram\nGrade 1: restless, sleep disturbed, irritable/agitated, tremor, impaired handwriting, 5 cps waves\nGrade 2: lethargic, time-disoriented, inappropriate, asterixis, ataxia, slow triphasic waves\nGrade 3: somnolent, stuporous, place-disoriented, hyperactive reflexes, rigidity, slower waves\nGrade 4: unrousable coma, no personality/behavior, decerebrate, slow 2-3 cps delta activity)\n\nThe Child-Pugh Score is calculated by summing the points for each criterion.",
        "example": "Patient: total bilirubin 2.5 mg/dL, albumin 3.0 g/dL, INR 1.8, moderate ascites, grade 2 encephalopathy.\nStep 1 - Bilirubin 2.5 mg/dL (2-3): +2 points.\nStep 2 - Albumin 3.0 g/dL (2.8-3.5): +2 points.\nStep 3 - INR 1.8 (1.7-2.3): +2 points.\nStep 4 - Ascites moderate: +3 points.\nStep 5 - Encephalopathy grade 2: +2 points.\nTotal Child-Pugh Score = 2 + 2 + 2 + 3 + 2 = 11 (Class C)."
    },

## 10
    {
        "calculator id": 16,
        "calculator name": "Wells' Criteria for DVT",
        "category": "risk",
        "output type": "integer",
        "question": "What is the patient's Wells' criteria score for Deep Vein Thrombosis?",
        "formula": "The criteria for the Wells' Criteria for Deep Vein Thrombosis (DVT) score are listed below:\n\n1. Active cancer (treatment or palliation within 6 months): No = 0 points, Yes = +1 point\n2. Bedridden recently >3 days or major surgery within 12 weeks: No = 0 points, Yes = +1 point\n3. Calf swelling >3 cm compared to the other leg (measured 10 cm below tibial tuberosity): No = 0 points, Yes = +1 point\n4. Collateral (nonvaricose) superficial veins present: No = 0 points, Yes = +1 point\n5. Entire leg swollen: No = 0 points, Yes = +1 point\n6. Localized tenderness along the deep venous system: No = 0 points, Yes = +1 point\n7. Pitting edema, confined to symptomatic leg: No = 0 points, Yes = +1 point\n8. Paralysis, paresis, or recent plaster immobilization of the lower extremity: No = 0 points, Yes = +1 point\n9. Previously documented DVT: No = 0 points, Yes = +1 point\n10. Alternative diagnosis to DVT as likely or more likely: No = 0 points, Yes = -2 points\n\nThe total score is calculated by summing the points for each criterion",
        "example": "Patient: active cancer, bedridden 4 days, calf swelling 4 cm > other leg, localized tenderness along deep veins, no prior DVT, alternative diagnosis unlikely.\nStep 1 - Active cancer: +1\nStep 2 - Bedridden >3 days: +1\nStep 3 - Calf swelling >3 cm: +1\nStep 4 - Collateral superficial veins: No = 0\nStep 5 - Entire leg swollen: No = 0\nStep 6 - Localized tenderness: +1\nStep 7 - Pitting edema: No = 0\nStep 8 - Paralysis/plaster: No = 0\nStep 9 - Prior DVT: No = 0\nStep 10 - Alternative diagnosis more likely: No = -2. So 0.\nTotal = 1 + 1 + 1 + 1 = 4."
    },

## 11
    {
        "calculator id": 22,
        "calculator name": "Maintenance Fluids Calculations",
        "category": "physical",
        "output type": "decimal",
        "question": "Based on the patient's weight, what is the patient's maintenance fluid in mL/hr?",
        "formula": "For patients whose weight is **10 kg or less**, the formula for computing the maintenance fluid is:   4 mL/kg/hr * weight (in kilograms).\n For patients whose weight is between 11 kg and 20 kg, the formula for computing the maintenance fluid is: 40 mL/hr + 2 mL/kg/hr * (weight (in kilograms) - 10 kilograms)\n For patients whose weight is greater than 20 kg, the formula for computing the maintenance fluid is:  60 mL/hr + 1 mL/kg/hr * (weight (in kilograms) - 20 kilograms)",
        "example": "Patient: weight 30 kg.\nSince weight > 20 kg: Maintenance fluid = 60 + 1 * (30 - 20) = 60 + 10 = 70 mL/hr."
    },

## 12
    {
        "calculator id": 23,
        "calculator name": "MELD Na (UNOS/OPTN)",
        "category": "lab",
        "output type": "decimal",
        "question": "What is the patient's MELDA Na score?",
        "formula": "The formula for computing the MELD Na is to first apply the following equation: MELD(i) = 0.957 x ln(Cr) + 0.378 x ln(bilirubin) + 1.120 x ln(INR) + 0.643.\nIf the MELD(i) is greater than 11 after rounding to the nearest tenth and multiplying the MELD(i) by 10, we apply the following equation: MELD = MELD(i) + 1.32 x (137 - Na) -  [ 0.033 x MELD(i) x (137 - Na)]. The MELD Na score is capped at 40. The concentration of Na is mEq/L, the concentration of bilirubin is mg/dL, and the concentration of creatinine is mg/dL. If the patient's Na concentration is less than 125 mEq/L, we set it to 125 mEq/L and if the patient's the Na concentration is greater 137 mEq/L, we round it to 137 mEq/L.",
        "example": "Patient: creatinine 1.5 mg/dL, bilirubin 3.0 mg/dL, INR 1.6, Na 132 mEq/L.\nStep 1 - MELD(i) = 0.957 * ln(1.5) + 0.378 * ln(3.0) + 1.120 * ln(1.6) + 0.643\nStep 2 - = 0.957 * 0.405 + 0.378 * 1.099 + 1.120 * 0.470 + 0.643\nStep 3 - = 0.388 + 0.415 + 0.526 + 0.643 = 1.972\nStep 4 - Round MELD(i)*10 = 19.7. Since 19.7 > 11, apply Na adjustment.\nStep 5 - MELD = 1.972 + 1.32 * (137 - 132) - 0.033 * 1.972 * (137 - 132)\nStep 6 - = 1.972 + 6.6 - 0.325 = 8.247. Score = 8.247 * 10 = 24.9 (capped at 40)."
    },

## 13
    {
        "calculator id": 25,
        "calculator name": "HAS-BLED Score for Major Bleeding Risk",
        "category": "risk",
        "output type": "integer",
        "question": "What is the patient's HAS-BLED score?",
        "formula": "The criteria for the HAS-BLED score are listed below below:\n\n1. Hypertension (Uncontrolled, >160 mmHg systolic): No = 0 points, Yes = +1 point\n2. Renal disease (Dialysis, transplant, Cr >2.26 mg/dL or >200 µmol/L): No = 0 points, Yes = +1 point\n3. Liver disease (Cirrhosis or bilirubin >2x normal with AST/ALT/AP >3x normal): No = 0 points, Yes = +1 point\n4. Stroke history: No = 0 points, Yes = +1 point\n5. Prior major bleeding or predisposition to bleeding: No = 0 points, Yes = +1 point\n6. Labile INR (Unstable/high INRs, time in therapeutic range <60%): No = 0 points, Yes = +1 point\n7. Age >65: No = 0 points, Yes = +1 point\n8. Medication usage predisposing to bleeding (Aspirin, clopidogrel, NSAIDs): No = 0 points, Yes = +1 point\n9. Alcohol use (≥8 drinks/week): No = 0 points, Yes = +1 point\n\nThe total HAS-BLED score is calculated by summing the points for each criterion.",
        "example": "Patient: 70-year-old on warfarin with uncontrolled hypertension (165 mmHg), prior stroke, history of liver disease, Cr 2.5 mg/dL, drinks 10 beers/week.\nStep 1 - Hypertension >160: +1\nStep 2 - Renal disease (Cr >2.26): +1\nStep 3 - Liver disease: +1\nStep 4 - Stroke history: +1\nStep 5 - Prior bleeding: 0\nStep 6 - Labile INR: 0\nStep 7 - Age >65: +1\nStep 8 - Medication (aspirin): 0 (unspecified)\nStep 9 - Alcohol ≥8/week: +1\nTotal HAS-BLED Score = 1 + 1 + 1 + 1 + 1 + 1 = 6."
    },

## 14
    {
        "calculator id": 27,
        "calculator name": "Glasgow-Blatchford Bleeding Score (GBS)",
        "category": "risk",
        "output type": "integer",
        "question": "What is the patient's Glasgow-Blatchford Bleeding score?",
        "formula": "The criteria for the Glasgow-Blatchford Bleeding Score are listed below:\n\n1. BUN (mg/dL): <18.2 = 0 points, 18.2-22.3 = +2 points, 22.4-28 = +3 points, 28-70 = +4 points, >70 = +6 points\n2. Hemoglobin (g/dL) for men: >=13 = 0 points, <=12-13 = +1 point, <=10-12 = +3 points, <10 = +6 points\n3. Hemoglobin (g/dL) for women: >=12 = 0 points, <=10-12 = +1 point, <10 = +6 points\n4. Systolic blood pressure (mm Hg): ≥110 = 0 points, 100-109 = +1 point, 90-99 = +2 points, <90 = +3 points\n5. Pulse ≥100 (per minute): No = 0 points, Yes = +1 point\n6. Melena present: No = 0 points, Yes = +1 point\n7. Presentation with syncope: No = 0 points, Yes = +2 point\n8. Liver disease history: No = 0 points, Yes = +2 point\n9. Cardiac failure present: No = 0 points, Yes = +2 point\n\nThe total Glasgow-Blatchford Score is calculated by summing the points for each criterion.",
        "example": "Patient: BUN 30 mg/dL, hemoglobin 11 g/dL (male), systolic BP 100 mmHg, pulse 105, melena present, no syncope, no liver disease, no cardiac failure.\nStep 1 - BUN 30 (28-70): +4\nStep 2 - Hemoglobin 11 (10-12 for men): +3\nStep 3 - SBP 100-109: +1\nStep 4 - Pulse ≥100: +1\nStep 5 - Melena: +1\nStep 6 - Syncope: 0\nStep 7 - Liver disease: 0\nStep 8 - Cardiac failure: 0\nTotal GBS = 4 + 3 + 1 + 1 + 1 = 10."
    },

## 15
    {
        "calculator id": 30,
        "calculator name": "Serum Osmolality",
        "category": "lab",
        "output type": "decimal",
        "question": "What is the patient's serum osmolality in terms of mOsm/kg?",
        "formula": "The formula for computing serum osmolality is 2 * Na + (BUN / 2.8) + (glucose / 18), where Na is the concentration of sodium in mmol/L, the concentration of BUN is in mg/dL, and the concentration of glucose is in mg/dL.",
        "example": "Patient: Na 140 mmol/L, BUN 20 mg/dL, glucose 100 mg/dL.\nSerum osmolality = 2 * 140 + (20 / 2.8) + (100 / 18) = 280 + 7.14 + 5.56 = 292.7 mOsm/kg."
    },

## 16
    {
        "calculator id": 33,
        "calculator name": "FeverPAIN Score for Strep Pharyngitis",
        "category": "diagnosis",
        "output type": "integer",
        "question": "What is the patient's FeverPAIN score?",
        "formula": "The criteria for the FeverPAIN score are listed below:\n    \n1. Fever in past 24 hours: No = 0 points, Yes = +1 point\n2. Absence of cough or coryza: No = 0 points, Yes = +1 point\n3. Symptom onset ≤3 days: No = 0 points, Yes = +1 point\n4. Purulent tonsils: No = 0 points, Yes = +1 point\n5. Severe tonsil inflammation: No = 0 points, Yes = +1 point\n\nThe FeverPAIN score is calculated by summing the points for each criterion.",
        "example": "Patient: fever in past 24 hours, no cough, symptoms started 2 days ago, purulent tonsils with severe inflammation.\nStep 1 - Fever: +1\nStep 2 - No cough/coryza: +1\nStep 3 - Onset ≤3 days: +1\nStep 4 - Purulent tonsils: +1\nStep 5 - Severe inflammation: +1\nTotal FeverPAIN Score = 1 + 1 + 1 + 1 + 1 = 5."
    },

## 17
    {
        "calculator id": 48,
        "calculator name": "PERC Rule for Pulmonary Embolism",
        "category": "diagnosis",
        "output type": "integer",
        "question": "What are the number of criteria met for the PERC Rule for Pulmonary Embolism (PE)?",
        "formula": "The PERC Rule critiera are listed below:\n\n1. Age ≥50: No = 0 points, Yes = +1 point\n2. Heart Rate (HR) ≥100: No = 0 points, Yes = +1 point\n3. O₂ saturation on room air <95%: No = 0 points, Yes = +1 point\n4. Unilateral leg swelling: No = 0 points, Yes = +1 point\n5. Hemoptysis: No = 0 points, Yes = +1 point\n6. Recent surgery or trauma (within 4 weeks, requiring treatment with general anesthesia): No = 0 points, Yes = +1 point\n7. Prior pulmonary embolism (PE) or deep vein thrombosis (DVT): No = 0 points, Yes = +1 point\n8. Hormone use (oral contraceptives, hormone replacement, or estrogenic hormone use in males or females): No = 0 points, Yes = +1 point\n\nThe total number of criteria met is taken by summing the points for each criterion.",
        "example": "Patient: 45-year-old with HR 95, O2 sat 97% on room air, no leg swelling, no hemoptysis, no recent surgery, no prior PE/DVT, not on hormones.\nStep 1 - Age ≥50: No = 0\nStep 2 - HR ≥100: No = 0\nStep 3 - O2 sat <95%: No = 0\nStep 4 - Unilateral leg swelling: No = 0\nStep 5 - Hemoptysis: No = 0\nStep 6 - Recent surgery/trauma: No = 0\nStep 7 - Prior PE/DVT: No = 0\nStep 8 - Hormone use: No = 0\nTotal PERC criteria met = 0 (PERC negative, no further testing needed)."
    },

## 18
    {
        "calculator id": 51,
        "calculator name": "SIRS Criteria",
        "category": "diagnosis",
        "output type": "integer",
        "question": "What is the number of SIRS critiera met by the patient?",
        "formula": "The rules for SIRS Criteria are listed below:\n    \n1. Temperature >38°C (100.4°F) or <36°C (96.8°F): No = 0 points, Yes = +1 point\n2. Heart rate >90: No = 0 points, Yes = +1 point\n3. Respiratory rate >20 or PaCO₂ <32 mm Hg: No = 0 points, Yes = +1 point\n4. White blood cell count (WBC) >12,000/mm³, <4,000/mm³, or >10% bands: No = 0 points, Yes = +1 point\n\nThe total number of criteria met is taken by summing the score for each criteria.",
        "example": "Patient: temperature 39°C, heart rate 100 bpm, respiratory rate 22, WBC 13,000/mm³.\nStep 1 - Temperature >38°C: Yes = +1\nStep 2 - Heart rate >90: Yes = +1\nStep 3 - RR >20: Yes = +1\nStep 4 - WBC >12,000: Yes = +1\nTotal SIRS criteria met = 4."
    },

## 19
    {
        "calculator id": 24,
        "calculator name": "Steroid Conversion Calculator",
        "category": "dosage",
        "output type": "decimal",
        "question": "Based on the patient's dose of a source corticosteroid (specify drug and route), what is the equivalent dosage in mg of a target corticosteroid (specify drug and route) using the standard conversion factors provided?",
        "formula": "The Steroid Conversions providing equivalent doses for various corticosteroids are listed below:\n1. Betamethasone: Route = IV, Equivalent Dose = 0.75 mg\n2. Cortisone: Route = PO, Equivalent Dose = 25 mg\n3. Dexamethasone (Decadron): Route = IV or PO, Equivalent Dose = 0.75 mg\n4. Hydrocortisone: Route = IV or PO, Equivalent Dose = 20 mg\n5. MethylPrednisoLONE: Route = IV or PO, Equivalent Dose = 4 mg\n6. PrednisoLONE: Route = PO, Equivalent Dose = 5 mg\n7. PredniSONE: Route = PO, Equivalent Dose = 5 mg\n8. Triamcinolone: Route = IV, Equivalent Dose = 4 mg",
        "example": "Patient: currently on Dexamethasone PO 6 mg/day.\nStep 1 - Dexamethasone equivalent dose = 0.75 mg.\nStep 2 - PrednisoLONE equivalent dose = 5 mg.\nStep 3 - Conversion factor: 5 / 0.75 = 6.67.\nStep 4 - Equivalent PrednisoLONE dose = 6 * 6.67 = 40 mg/day."
    },
## 20
    {
        "calculator id": 13,
        "calculator name": "Estimated Due Date",
        "category": "date",
        "output type": "date",
        "question": "Using Naegele's Rule for estimated due date based on the last menstrual period and cycle length, what is the the patient's estimated due date? Your response should be in the format of M/D/Y (ie 08/31/2023, 07/03/2000) with just the date and not other text. ",
        "formula": "The patient's estimated due date based on their last menstrual period and cycle length is computed by using Naegele's Rule. Estimated Due Date (EDD) = Last Menstrual Period (LMP) date + 280 + (cycle_length - 28) days",
        "example": "Patient: LMP date = 05/15/2023, cycle length = 28 days.\nEDD = 05/15/2023 + 280 - (28 - 28) = 05/15/2023 + 280 = 02/19/2024."
    },
    
## 21

## 22

## 23

## 24

## 25

## 26

## 27

## 28

## 29

## 30

## 31

## 32

## 33

## 34