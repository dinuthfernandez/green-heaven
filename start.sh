#!/bin/bash
exec gunicorn -w 1 --bind 0.0.0.0:$PORT app:app --timeout 120