# Local build: results -> figures -> Word + PowerPoint (GitHub Pages serves the repo root as-is).
.PHONY: all test results figures docx pptx garch kalman data serve clean

all: test results figures docx pptx garch kalman

test:
	python3 model/test_models.py
	python3 model/test_kalman.py
	python3 model/test_garch.py

results:
	python3 model/run_experiment.py

figures:
	python3 tools/make_figures.py

docx:
	python3 tools/build_docx.py

pptx:
	python3 tools/build_pptx.py

# GARCH study on real daily data (the chosen project direction)
garch:
	python3 model/run_garch.py
	python3 tools/make_garch_figures.py

# Kalman prototype on real data (backup direction) (data/french_monthly.csv is committed; `make data` refreshes it)
kalman:
	python3 model/run_kalman.py
	python3 tools/make_kalman_figures.py

data:
	python3 tools/fetch_french.py

serve:
	python3 -m http.server 8623

clean:
	rm -rf build
