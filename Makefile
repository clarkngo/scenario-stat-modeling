# Local build: results -> figures -> Word + PowerPoint (GitHub Pages serves the repo root as-is).
.PHONY: all test results figures docx pptx serve clean

all: test results figures docx pptx

test:
	python3 model/test_models.py

results:
	python3 model/run_experiment.py

figures:
	python3 tools/make_figures.py

docx:
	python3 tools/build_docx.py

pptx:
	python3 tools/build_pptx.py

serve:
	python3 -m http.server 8623

clean:
	rm -rf build
