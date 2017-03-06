if [ -z "$1" ]; then
  python -m unittest -v agent_test.Project1Test
else
  python -m unittest -v agent_test.Project1Test.$1
fi
