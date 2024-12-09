# Copyright (C) 2024 Aleksei Rogov <alekzzzr@gmail.com>. All rights reserved.

run:
	uvicorn app.main:app --reload --host 0.0.0.0

build:
	docker build -t thermo .
