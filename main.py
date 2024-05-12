import os
import uuid
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from ctypes import windll
from tkinter import filedialog, Tk, Label, Button, messagebox
import PyPDF2

# Required terminal commands:
# pip install elevenlabs
# pip install python-dotenv
# List of possible voices taken from https://api.elevenlabs.io/v1/voices

# To fix blurry tkinter font AND blurry pop-up box when uploading img file. Taken from https://stackoverflow.com
# /questions/41315873/attempting-to-resolve-blurred-tkinter-text-scaling-on-windows-10-high-dpi-disp
# /43046744#43046744
windll.shcore.SetProcessDpiAwareness(1)


class PDFTextToSpeech:
    def __init__(self):
        # For Text-to-speech conversion
        self.api_key = os.environ.get("API_KEY")
        self.voice_id = "JBFqnCBsd6RMkjVDRZzb"
        self.api_url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        self.el_client = ElevenLabs(api_key=self.api_key)
        self.save_file_path = None
        self.text = None
        self.error = False

        # For user to upload PDF File via tkinter window
        self.title_label_default = "Upload your PDF!"

        self.window = Tk()
        self.window.title("PDF Text Extractor and Text-to-Speech Converter")
        self.window.minsize(width=500, height=500)
        self.window.config(padx=20, pady=20)

        self.title_label = Label(text=self.title_label_default, font=("Calibri", 30, "bold"))
        self.title_label.config(padx=20)
        self.title_label.pack()

        self.info_label = Label(text=("This is a text-to-speech converter which extracts text from your PDF "
                                      "into an audio file. Press the button to upload your PDF. "),
                                font=("Calibri", 20, "normal"), wraplength=600)
        self.info_label.config(padx=20, pady=20)
        self.info_label.pack()

        self.upload_button = Button(text="Upload PDF", font=("Arial", 16, "normal"),
                                    command=self.convert_pdf_tts)
        self.upload_button.pack()

        self.window.mainloop()

    def text_to_speech_file(self):
        # Calling the text_to_speech conversion API with detailed parameters
        response = self.el_client.text_to_speech.convert(
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            optimize_streaming_latency="0",
            output_format="mp3_22050_32",
            text=self.text,
            model_id="eleven_turbo_v2",
            voice_settings=VoiceSettings(
                stability=1.0,
                similarity_boost=1.0,
                style=1.0,
                use_speaker_boost=True,
            ),
        )

        with open(self.save_file_path, "wb") as f:
            for chunk in response:
                if chunk:
                    f.write(chunk)

        messagebox.showinfo(title="Conversion successful!", message=f"A new audio file was saved successfully! "
                                                                    f"It is in the same location as your PDF file "
                                                                    f"at {self.save_file_path}.")
        # Return the path of the saved audio file
        return self.save_file_path

    def extract_text_from_pdf(self):
        upload_file_path = filedialog.askopenfilename(filetypes=(("PDF files", "*.pdf"),))
        directory = os.path.dirname(upload_file_path)
        self.save_file_path = f"{directory}/{uuid.uuid4()}.mp3"
        if upload_file_path:
            text = self.extract_text(upload_file_path)
            self.text = text

    def extract_text(self, pdf_file):
        try:
            with open(pdf_file, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                num_pages = len(pdf_reader.pages)
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    self.text = page.extract_text()
        except Exception as e:
            messagebox.showerror(title="Error", message=f"Error: {e}")
            self.error = True
        return self.text

    def convert_pdf_tts(self):
        self.error = False
        self.title_label.config(text="Converting...")
        self.extract_text_from_pdf()
        if self.error is False:
            self.text_to_speech_file()

        self.title_label.config(text=self.title_label_default)


converter = PDFTextToSpeech()
