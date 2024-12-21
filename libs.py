import os
from typing import Any, Dict, Iterable, List, Optional
from dotenv import load_dotenv
from loguru import logger
import google.generativeai as genai
import PIL.Image
import json