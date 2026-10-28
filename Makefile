.PHONY: test run verify-tensor clean

test:
	python3 run_tests.py

run:
	PYTHONPATH=src uvicorn chakravyuh.main:app --host 0.0.0.0 --port 8000 --reload

verify-tensor:
	PYTHONPATH=src python3 -c "from chakravyuh.voice.vachana_vc import VachanaVoiceCloneEngine; t, m = VachanaVoiceCloneEngine().extract_speaker_embedding(); print('Shape:', t.shape, 'Dtype:', t.dtype, 'Bytes:', t.nbytes, 'BitInvariant:', t.verify_bfloat16_bit_invariant())"

clean:
	find . -name "__pycache__" -type d -exec rm -rf {} +
