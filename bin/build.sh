# Mac
env PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.10.8
pyenv rehash
pyenv exec python -m pip install -r requirements.txt
pyenv exec python -m pip install pyinstaller
pyenv exec pyinstaller volt.spec

# Windows, from mac/linux
wine python -m pip install -r requirements.txt
wine python -m pip install pyinstaller
wine python -m PyInstaller volt.spec
