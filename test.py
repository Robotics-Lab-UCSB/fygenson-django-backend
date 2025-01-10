import fasttext

model = fasttext.load_model("./models/general_intent_model.bin")
print(model.predict("where is the circular thermometer?"))