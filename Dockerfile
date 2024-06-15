FROM continuumio/miniconda3

# 更新 conda
RUN conda update -n base -c defaults conda

# Create a non-root user
RUN adduser --disabled-password --gecos "" appuser

WORKDIR /app
COPY . /app

# Install the required system packages
RUN apt-get update && \
    apt-get install -y curl software-properties-common git && \
    rm -rf /var/lib/apt/lists/* 

# Install the required python packages
RUN conda create -n chat2scenario python=3.9 && \
    conda clean --all --yes && \
    conda install -c conda-forge build-essential && \
    conda activate chat2scenario && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    conda clean --all --yes

# Switch to the non-root user
USER appuser

# EXPOSE 8501

# HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
