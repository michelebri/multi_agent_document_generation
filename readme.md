# Large Language Models Based Generation of Semi-structured Documents from Semantically Similar Examples in the Public Administration Domain

## Abstract
> Abstract

[TODO: INSERT LINK TO PAPER]: #

Paper: <a href="" target="_blank">Large Language Models Based Generation of Semi-structured Documents from Semantically Similar Examples in the Public Administration Domain</a>

## Pipeline

[TODO: INSERT DESCRIPTION OF PIPELINE]: #
## Results

[TODO: insert results here]: #

<span style="color:green"> *Result description here*</span>
<br />
<span style="color:red"> *Result pictures tables and graphs here*</span>

# Framework
## Install

> [!IMPORTANT] 
> Make sure you have installed ==conda==, ==Python 3.8.0== and the ==pip== package manager.

### Create the virtual environment
 Create a conda environment
 ```
 conda create --name "<ENVIRONMENT_NAME>" python=3.8.0
 ```
 then switch to the environment with
 ```
 conda activate <ENVIRONMENT_NAME>
 ```

> [!WARNING]
> You have to make sure that the conda environment is activated before execution.

### Clone this repo
```
git clone https://github.com/michelebri/multi_agent_document_generation.git
```

### Preinstall cython and pyyaml
```
pip install "cython<3.0.0" wheel
pip install "pyyaml==6.0.0" --no-build-isolation
```

### Install `requirements.txt`
While in the repository main directory:
```
pip install -r requirements.txt
```

## Running

### Configure the execution environment
<span style="color:green"> *Insert a description of the env variables configuration*</span>

### Obtain the free Adobe API Key
Follow the guide at the link [link](https://developer.adobe.com/document-services/docs/overview/pdf-extract-api/quickstarts/python)

### LLM model configuration
If you have an OpenAI key insert it in the os enviroment variable

### Run
To run the framework launch the `generate.py` Python script:
```
python generate.py
```

