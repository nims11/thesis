MAIN = thesis

$(MAIN).pdf: $(MAIN).tex $(wildcard chapters/*.tex)
	pdflatex $(MAIN).tex && bibtex $(MAIN) && pdflatex $(MAIN).tex && pdflatex $(MAIN).tex

clean:
	rm -rf *~ *.tmp *.thm *.run.xml
	rm -f *.bbl *.blg *.aux *.auxlock *.end *.fls *.lo* *.out *.fdb_latexmk *.toc
	rm $(MAIN).pdf
