# Jira - Guru Detector

This repository is the implementation of a tool that will be able to recommend a "Guru" for anything that a person inside a company might need help with.

In order to achieve this, the company's Jira platform will be used as it holds precious data that can aid towards this goal.

This is the very early stage of the project. For the moment I want to create a "data_downloader" script that will be able to query the jira platform using REST api and gather the data into csv files that will be later processed in order to make it easy to extract features from them.

Prerequisites:

* JIRA

To-Do:

- Maybe add the requirements to a requirements.txt file and then add the instruction to use `pip install -r requirements.txt`


## Dataset Format
First of all, I think that it would be better to have to sets of datasets. The first one will have the "raw" information. For example, the code blocks will be included. In case we want to slightly alter our preprocessing, we can use those datasets so that we avoid having to contact the actual Jira Server through REST. The second set of datasets will contain the processed information.

The current idea of how the data will look like is that there will be a csv for each of the following:

### Summaries (Titles)
Not sure if this will eventually play an important role or not, given that many times the issues are raised by Project Managers or people from the Customer (eg. William Hill). For the latter, the solution is simple as we can filter by email address. I suppose that the Development Leads are the ones that usually tend to raise the tickets. So (maybe) including the summaries could be a quite "biased" feature.

The generated csv file will include:
- Ticket ID (eg. WIL-123)
- Summary (eg. "Telebet 2 - Display Customer Notes")
- Reporter (username or email of the creator)
- Creation Date (YYYY-MM-DD)