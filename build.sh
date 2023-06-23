# Mac
env PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.10.8
pyenv rehash
pyenv exec python -m pip install -r requirements.txt
pyenv exec python -m pip install pyinstaller
pyenv exec pyinstaller test_py.spec

# Windows, from mac/linux
wine python -m pip install -r requirements.txt
wine pyinstaller test_py.spec
