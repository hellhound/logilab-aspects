MKHTML=mkdoc
MKHTML_OPT=--doctype article --param toc.section.depth=1 --target=html --stylesheet=single-file

all: *.html

*.html: *.txt
	${MKHTML} ${MKHTML_OPT} *.txt

clean:
	rm -f *.html
