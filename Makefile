run:
	./game.py --log=info --windowed
run-detailed-log:
	./game.py --save_log_file --detailed_log_prefix --log=debug --windowed
tests:
	python -m doctest game.py -o ELLIPSIS
.PHONY: tags
tags:
	ctags -R .

