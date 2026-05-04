
.PHONY: all data features train forecast app clean \
        docker-build docker-up docker-down \
        dvc-push dvc-pull \
        tf-init tf-plan tf-apply \
        lint test ci

# ── Full local pipeline ────────────────────────────────────────────────────────
all: data features train forecast

# ── Data pipeline ──────────────────────────────────────────────────────────────
data:
	python src/collect.py
	python src/harmonize.py
	python src/impute.py

# ── Feature engineering ────────────────────────────────────────────────────────
features:
	python src/features.py
	python src/target.py

# ── Model training + tuning ────────────────────────────────────────────────────
train:
	python src/tune.py
	python src/train.py

# ── SHAP explainability ────────────────────────────────────────────────────────
explain:
	python src/explain.py

# ── Prophet forecasting ────────────────────────────────────────────────────────
forecast:
	python src/forecast.py

# ── Streamlit app ──────────────────────────────────────────────────────────────
app:
	streamlit run app/app.py

# ── Setup ──────────────────────────────────────────────────────────────────────
install:
	pip install -r requirements.txt

# ── Code quality ───────────────────────────────────────────────────────────────
lint:
	ruff check src/ app/ --fix
	ruff format src/ app/

test:
	pytest tests/ -v --ignore=tests/test_data_quality.py

ci: lint test

# ── Docker ────────────────────────────────────────────────────────────────────
docker-build:
	docker build -t global-livability-ai:latest .

docker-up:
	docker compose up --build

docker-down:
	docker compose down

docker-pipeline:
	docker compose run --rm pipeline

# ── DVC data versioning ───────────────────────────────────────────────────────
dvc-init:
	dvc init
	dvc remote add -d s3_datalake s3://gla-data-lake-dev

dvc-push:
	dvc add data/raw data/processed data/features models
	dvc push

dvc-pull:
	dvc pull

# ── Terraform ─────────────────────────────────────────────────────────────────
tf-init:
	cd terraform && terraform init

tf-plan:
	cd terraform && terraform plan -out=plan.tfplan

tf-apply:
	cd terraform && terraform apply plan.tfplan

tf-destroy:
	cd terraform && terraform destroy

# ── MLflow UI ─────────────────────────────────────────────────────────────────
mlflow-ui:
	mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000

# ── Clean generated artifacts ─────────────────────────────────────────────────
clean:
	rm -rf data/processed/* data/features/* models/* app/assets/*.png

