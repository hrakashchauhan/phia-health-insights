# PHIA: Transforming Wearable Data into Personal Health Insights using Large Language Model Agents

The official repository for paper "Transforming Wearable Data into Personal Health Insights using Large Language Model Agents" and the corresponding Personal Health Insights Agent (PHIA).

<p align="center">
:fire: Please remember to :star: this repo if you find it useful and <a href="https://github.com/yahskapar/PHIA#scroll-citation">cite</a> our work if you end up using it in your work! :fire:
</p>
<p align="center">
:fire: If you have any questions or concerns, please create an issue :memo:! :fire:
</p>

<p align="center">
<a href="https://research.google/blog/advancing-personal-health-and-wellness-insights-with-ai/">Blog Post</a> | <a href="https://arxiv.org/abs/2406.06464">Pre-print</a>
</p>

## :wrench: Setup

Run `bash setup.sh` to fully setup the phia conda environment. The entire setup process should be automatic from end-to-end, though has been tested on a limited number of machines. Please report any issues as you encounter them.

Once setup is complete, you can activate the environment using `conda activate phia` in your terminal for subsequent usage via the terminal. Most typical usage will involve invoking the conda environment, either via terminal or VSCode, as a kernel to utilize for various notebooks in the repo. If you open a notebook in VSCode, you should be able to select the phia environment as the kernel in the top-right corner.

## :computer: Usage

Notable parts of our repo is as follows:
- `figs` contains all code necessary to reproduce figures from the paper.
- `data` contains model outputs and human annotations.
- `Objective Query - PHIA.xlsx` contains 172 open-ended queries.
- `Open-Ended Query - PHIA.xlsx` contains 4000 objective queries.
- `synthetic_wearable_users` contains a set of synthetic wearable users. Subject 465, 333, 171 and 41 are used in evaluation.
- `few_shots` contains all of our few-shot examples that are utilized by PHIA.
- `phia_agent.py` contains the core agent logic for PHIA.
- `prompt_templats.py` contains key prompt templates (e.g., agent preamble) utilized by PHIA.
- `phia_demo.ipynb` contains code to try out PHIA. API keys must be provided as noted in the notebook.

Beyond referencing various artifacts, the primary runnable notebooks of interest in this repo are in the `figs` folder (for reproducing figures using source data) and in `phia_demo.ipynb` (for trying out PHIA). When trying out PHIA, take note of particular notebook cells and their purpose, especially what data (e.g., synthetic user summary dataframe, exercise dataframe) is being loaded and whether or not you want to change what data is being loaded.

Note: you can obtain a Google / Gemini API key from [here](https://aistudio.google.com) with certain rate limits. Similarly, tavily offers a free usage tier and corresponding API key for researchers [here](https://www.tavily.com/#pricing).

## :scroll: Citation
If you find our [paper](https://arxiv.org/abs/2406.06464) or this code release useful for your research, please cite our work.

```
@article{merrill2024transforming,
  title={Transforming wearable data into health insights using large language model agents},
  author={Merrill, Mike A and Paruchuri, Akshay and Rezaei, Naghmeh and Kovacs, Geza and Perez, Javier and Liu, Yun and Schenck, Erik and Hammerquist, Nova and Sunshine, Jake and Tailor, Shyam and others},
  journal={arXiv preprint arXiv:2406.06464},
  year={2024}
}
```

## License
```
Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)
```
