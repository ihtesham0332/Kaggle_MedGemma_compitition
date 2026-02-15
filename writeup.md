# MedGemma Kidney Stone Agent: The "Split-Brain" Radiologist
## A Multi-Window Agentic Approach to Nephrolithiasis Diagnosis

### 🚀 Project Overview
Kidney stones (nephrolithiasis) affect ~10% of the global population, yet diagnosis remains a manual, error-prone process. Radiologists must mentally fuse multiple CT "windows" (Bone, Soft Tissue, Lung) to distinguish dense stones from phleboliths or vascular calcifications—a high-cognitive load task that leads to fatigue and missed diagnoses.

**I built the MedGemma Kidney Stone Agent to solve this.**

Unlike traditional "black box" AI classifiers that give a simple Yes/No, this is an **Agentic Radiologist** that leverages **Google's MedGemma 1.5 4B-it** to:
1.  **"See" like a specialist** using a novel "Split-Brain" multi-channel encoding.
2.  **Reason clinically** to extract stone size, location, and urgency.
3.  **Communicate** via a generated medical report and an interactive Q&A consultation session.

---

### 🧠 The "Secret Sauce": Split-Brain Preprocessing
The core innovation of this project is **Split-Brain Multi-Channel Encoding**. Standard AI models treat CT scans as grayscale images, losing critical density information. My pipeline encodes three distinct radiologist "views" into the RGB channels of a single image, allowing MedGemma to analyze density and context simultaneously.

| Channel | Clinical Window | Settings (W/L) | Purpose |
| :--- | :--- | :--- | :--- |
| **🔴 Red** | **Wide Window** | W:2000, L:0 | Provides global anatomical context and anchors the scan. |
| **🟢 Green** | **Soft Tissue** | W:400, L:50 | Visualizes the kidney parenchyma, ureters, and inflammation. |
| **🔵 Blue** | **Bone Window** | W:1800, L:400 | Max contrast for **stones** (calcium) vs. soft tissue. |

**Why this works:** The model receives a hyper-informative image where stones "pop" in blue/cyan against the soft-tissue green background, drastically improving detection accuracy without needing 3D volumes.

---

### 🛠️ Technical Architecture

#### 1. The Brain: MedGemma 1.5 4B-it
I chose **MedGemma 1.5** for its superior biomedical reasoning capabilities. By using the **4B-it (Instruction Tuned)** variant, I created an agent that follows a strict system prompt to output structured JSON data *and* natural language summaries.
*   **Safety:** The model is prompted to assess "Urgency" (Low/Medium/High) to triage patients effectively.
*   **Efficiency:** Running in 4-bit quantization allows this powerful system to deploy on consumer-grade hardware (or free Kaggle GPUs).

#### 2. The Body: FastAPI Backend
The inference engine is wrapped in a high-performance **FastAPI** server that handles:
*   **DICOM Ingestion:** automatically converting raw medical `.dcm` files into the "Split-Brain" tensors.
*   **Session Management:** Maintaining context for follow-up Q&A.

#### 3. The Face: Streamlit Clinician Dashboard
The UI is designed for real-world clinical use:
*   **Drag-and-Drop Analysis:** Supports raw DICOMs or standard images.
*   **Instant Reporting:** Generates a structured "Medical Report" with Stone Size (mm) and Location.
*   **Interactive Consultation:** A chat interface where doctors can ask, *"Is this stone passable?"* or *"Compare this to the left kidney"*, leveraging the model's textual understanding.

---

### 🌍 Impact & Future Work
This tool democratizes expert-level radiology. In low-resource settings where sub-specialist radiologists are scarce, the MedGemma Agent acts as a "second pair of eyes," ensuring that urgency is flagged immediately.

**Future Roadmap:**
*   **3D Volumetric Analysis:** Extending the generic split-brain approach to sequential slices.
*   **LMM-RAG:** integrating patient history (PDFs) into the context window for holistic diagnosis.

---

### 💻 How to Run
The project is containerized and ready for deployment.
1.  **Clone the Repo**
2.  **Install Dependencies:** `pip install -r requirements.txt`
3.  **Run the Agent:** `run_app.bat`

*Powered by Google MedGemma 1.5, Streamlit, and FastAPI.*
