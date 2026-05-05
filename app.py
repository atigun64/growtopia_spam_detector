import joblib
import gradio as gr

# load once at startup
model = joblib.load("spam_model.joblib")

def predict_probability(model, text):
    # replace this with your real logic if needed
    # examples:
    #   return model.predict_proba([text])[0][1]
    #   return model.predict_proba(vectorizer.transform([text]))[0][1]
    prob = model.predict_proba([text])[0][1]
    return float(prob)

def predict(text):
    if not text or not text.strip():
        return "Please enter a message."

    prob = predict_probability(model, text)
    label = int(prob >= 0.5)

    if prob >= 0.9:
        verdict = "very likely spam"
    elif prob >= 0.7:
        verdict = "likely spam"
    elif prob >= 0.5:
        verdict = "maybe spam"
    else:
        verdict = "probably normal"

    return f"spam_probability={prob:.4f} label={label}\n{verdict}"

demo = gr.Interface(
    fn=predict,
    inputs=gr.Textbox(lines=4, placeholder="Type a message..."),
    outputs=gr.Textbox(lines=4),
    title="Spam Detector Demo",
    description="Paste a message and get a spam score.",
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
