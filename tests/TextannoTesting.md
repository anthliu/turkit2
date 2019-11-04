# Getting Text Classification to work

Turkit2 is a project that takes a static webpage template, posts the template to mturk, and parses the results that come from mturk.

I've set up a test script that posts a (dummy) classification task to mturk sandbox, and prints the sandbox link for you to view.
To use, make sure you are on the `textanno` branch: `git checkout textanno`.
```
cd tests
python textanno.py
```

The template is written and can be modified in `tests/textanno_schema.html`.
