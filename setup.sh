#/usr/bin/env bash -e

VENV=venv

if [ ! -d "$VENV" ]
then

    PYTHON=`which python3`

    if [ ! -f $PYTHON ]
    then
        echo "could not find python"
    fi
    virtualenv -p $PYTHON $VENV

fi

. $VENV/bin/activate

pip install -r requirements.txt

if [ -f config.ini ]
then
    rm -rf config.ini
fi

if [ -f /usr/share/snips/assistant/snippets/ndy1982.Homematic/config.ini ]
then
    cp /usr/share/snips/assistant/snippets/ndy1982.Homematic/config.ini config.ini
else
    cp config.ini.default config.ini
fi
