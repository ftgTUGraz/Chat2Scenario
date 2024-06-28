# Chat2Scenario: Scenario Extraction From Dataset Through Utilization of Large Language Model

## 🚨 Important News 🚨

**June 17, 2024**: The web app "chat2scenario" is accessiable via [https://chat2scenario.streamlit.app/](https://chat2scenario.streamlit.app/)

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
@misc{zhao2024chat2scenario,
      title={Chat2Scenario: Scenario Extraction From Dataset Through Utilization of Large Language Model}, 
      author={Yongqi Zhao and Wenbo Xiao and Tomislav Mihalj and Jia Hu and Arno Eichberger},
      year={2024},
      eprint={2404.16147},
      archivePrefix={arXiv},
      primaryClass={cs.RO}
}
```

## Usage
### Without installation
- You can directly access the web app via the following link: [https://chat2scenario.streamlit.app/](https://chat2scenario.streamlit.app/)

### With installation
- Follow the installation and operation instructions to download the source code and use it locally.

## Installation
### Pre-requirements
- Python installation
	- This repository is developed under python 3.9.19 in Anaconda.
- Application for dataset
	- The highD dataset can be applied via (https://levelxdata.com/highd-dataset/).
- [OpenAI API key](https://help.openai.com/en/articles/4936850-where-do-i-find-my-api-key) 
### Clone this repository
```bash
git clone https://github.com/ftgTUGraz/Chat2Scenario.git 
```
### Install all required packages
#### Method 1 - in your original environment
```bash
pip install -r requirements.txt
```
#### Method 2 - create a new environment through yml file
```bash
conda env create -f environment.yml
conda activate chat2scenario
```

## Operation
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
	- Click "Extract original scenario" to start extraction process.
	- After the progress bar reaches to 100\%, click "download" to acquire the xosc files. 
- (Optional) Modify the path 
	- If necessary, modify the path of RoadNetWork in the generated OpenSCENARIO.
```xml
<RoadNetwork>
    <LogicFile filepath="../xodr/highD_01_highway.xodr"/>
</RoadNetwork>
```
- Visualization
	- Replay the xosc in Esmini based on the [userguide](https://esmini.github.io/#_view_a_scenario)
	- Replay the txt file in CarMaker based on the [Q&A](https://www.ipg-automotive.com/en/support/support-request/faq/usage-of-user-inputs-from-a-file-in-a-maneuver-133/) 

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

For help or issues using the code, please create an issue in this repository or contact Yongqi Zhao at [yongqi.zhao@tugraz.at](mailto:yongqi.zhao@tugraz.at), contact Wenbo Xiao at [wenbo.xiao@student.tugraz.at](wenbo.xiao@student.tugraz.at). 
You can also ask questions in our SLACK Workspace. **[Click here!](https://join.slack.com/t/chat2scenario/shared_invite/zt-2hwtat65j-c2EqeGGewDJpWRBpPUhNDw)**

## Acknowledgement
- This work was supported by FFG in the research project PECOP (FFG Projektnummer 893988) in the program "Bilateral Cooperation Austria - People's Republic of China/Most 2nd Call".

- The codebase is built upon other these previous codebases:<br>
	- [Environment Simulator Minimalistic (esmini)](https://github.com/esmini/esmini)<br>
	- [scenariogeneration](https://github.com/pyoscx/scenariogeneration)<br>
	- [streamlit](https://github.com/streamlit/streamlit)
