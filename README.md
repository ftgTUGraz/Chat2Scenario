# Chat2Scenario: Scenario Extraction From Dataset Through Utilization of Large Language Model

## Description

Chat2Scenario is a web-based tool that allows users to search for specific driving scenarios within a dataset by inputting descriptive functional scenario text. Results are presented in [ASAM OpenSCENARIO](https://www.asam.net/standards/detail/openscenario/) and [IPG CarMaker .txt](https://ipg-automotive.com/en/support/support-request/faq/usage-of-user-inputs-from-a-file-in-a-maneuver-133/) format. 
<table>
  <tr>
    <td><img src="docs/demo.gif" alt="exemplary scenario in Esmini" width="400" height="200" /></td>
    <td><img src="docs/demo_CM.gif" alt="exemplary scenario in CarMaker" width="400" height="200"/></td>
  </tr>
</table>

## Citation
```bibtex
@software{Chat2Scenario,
  author = {{Zhao, Yongqi}, {Xiao, Wenbo}},
  title = {{Chat2Scenario: Scenario Extraction From Dataset Through Utilization of Large Language Model}},
  url = {https://github.com/zhaoyongqi2022/Chat2Scenario.git},
  year = {2024}
}
```

## Installation
### Pre-requirements
- Python installation
	- This repository is developed under python 3.9.16 in Anaconda.
- Application for dataset
	- The highD dataset can be applied via (https://levelxdata.com/highd-dataset/).
- [OpenAI API key](https://help.openai.com/en/articles/4936850-where-do-i-find-my-api-key) 
### Clone this repository
```bash
git clone https://github.com/zhaoyongqi2022/Chat2Scenario.git 
```
### Install all required packages
#### method 1, in your original environment
```bash
pip install -r requirements.txt
```
#### create a new environment through conda env
```bash
conda env create -f environment.yml
conda activate chat2scenario
```

## Usage
- Open the Project
	- Open the entire project using a code editor e.g., Visual Studio Code
	- Run the project in the terminal with the following command
	```bash
	streamlit run .\Chat2Scenario-Web.py
	```
	- The Chat2Scenario web application will appear
![chat2scenario web](docs/Chat2Scenario_Web.png)
- Set Up Everything
	- Select "highD" dataset option (currently, only highD is compitable).
	- Upload the corresponding dataset (only the xx_tracks.csv file should be uploaded).
	- Select a criticality metric and specify the threshold.
	- Enter your OpenAI API Key.
	- Choose the desired scenario format.
	- Provide a descriptive text for the scenario e.g., "The ego vehicle maintains its lane and velocity. Initially, Target Vehicle #1 is driving in the left adjacent lane. It then accelerates and changes lanes to the right, eventually driving in front of the ego vehicle."
- Run
	- Click "Preview searched scenario" to search for and preview scenarios. 
	- Scenarios are ready for download when the prograss bar reaches 100%.
- Download
	- Specify the download path, e.g., C:\Users\ilovetug\Downloads.
	- Click "Extract original scenario" to download them. 
- (Optional) Modify the path 
	- If necessary, modify the path of RoadNetWork in the generated OpenSCENARIO.
```xml
<RoadNetwork>
    <LogicFile filepath="../xodr/highD_01_highway.xodr"/>
</RoadNetwork>
```

## Contributing
Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are greatly appreciated.
- Fork the project.
- Create your feature branch (git checkout -b feature/enhancement)
- Commit your changes (git commit -m 'add some enhacement')
- Push to the branch (git push origin feature/enhancement)
- Open a pull request

## Developers

* Yongqi Zhao ([yongqi.zhao@tugraz.at](mailto:yongqizhao@tugraz.at))
* Wenbo Xiao ([wenbo.xiao@student.tugraz.at](mailto:wenbo.xiao@student.tugraz.at))

For help or issues using the code, please create an issue in this repository or contact Yongqi Zhao at [yongqi.zhao@tugraz.at](mailto:yongqi.zhao@tugraz.at). 

## Acknowledgement
- This work was supported by FFG in the research project PECOP (FFG Projektnummer 893988) in the program "Bilateral Cooperation Austria - People's Republic of China/Most 2nd Call".

- The codebase is built upon other these previous codebases:<br>
	- [Environment Simulator Minimalistic (esmini)](https://github.com/esmini/esmini)<br>
	- [scenariogeneration](https://github.com/pyoscx/scenariogeneration)<br>
	- [streamlit](https://github.com/streamlit/streamlit)
