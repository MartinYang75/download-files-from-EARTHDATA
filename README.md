# NASA Earthdata CMR Downloader

A lightweight and efficient Python script to bulk download data from NASA's Earthdata portal using the Common Metadata Repository (CMR) API. 

It supports spatial and temporal filtering, automatic `.netrc` authentication configuration, and multi-threaded concurrent downloads with a progress bar.

## Features
* **Automated Authentication:** Reads credentials from a simple text file and safely configures your `~/.netrc` file for Earthdata login.
* **Smart Filtering:** Query datasets by short name, version, date range, and spatial bounding box.
* **Concurrent Downloads:** Uses `ThreadPoolExecutor` to download multiple files simultaneously, significantly speeding up the process.
* **Resume Capability:** Automatically skips files that have already been downloaded to your output directory.
* **Progress Tracking:** Displays a real-time progress bar using `tqdm`.

## Prerequisites

You need an [Earthdata Login](https://urs.earthdata.nasa.gov/) account to download NASA data. 

Install the required Python packages:
```bash
pip install requests tqdm
```

## Setup & Authentication

1. Create a text file named `earthdata_credentials.txt`.
2. Add your Earthdata username on the first line and your password on the second line:
    ```text
    your_username
    your_password
    ```
3. Update the `CRED_FILE` path in the script to point to this file:
    ```python
    CRED_FILE = '/path/to/your/earthdata_credentials.txt'
    ```

## Usage

1. Open `download_files_CMR_EN.py`.
2. Scroll down to the `if __name__ == "__main__":` block.
3. Modify the parameters in the `batch_download_cmr_data` function to fit your needs:
    * `short_name`: The dataset's short name (e.g., `OCO3_L2_Lite_FP`).
    * `version`: The dataset version (e.g., `11r`).
    * `temporal_range`: The time window `YYYY-MM-DD,YYYY-MM-DD`.
    * `bounding_box`: The spatial coverage `min_lon,min_lat,max_lon,max_lat`.
    * `output_dir`: Your local directory where files will be saved.

4. Run the script:
```bash
python download_files_CMR_EN.py
```
