import asyncio
import numpy as np
from sklearn.datasets import fetch_20newsgroups
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.stats import entropy
from turkit2.common import TextClassification
from turkit2.qualifications import Unique, Locale, AcceptRate
from utils import get_client

class ActiveLearner(object):
    def __init__(self, data, classes, model, repetitions=3, batch_size=10, price=0.1, starting_size=50, verbosity=0):
        self.client = get_client()

        self.data = np.array(data)
        self.classes = classes
        self.cls_to_idx = {cls: idx for idx, cls in enumerate(self.classes)}
        self.batch_size = batch_size
        self.repetitions = repetitions
        self.price = price
        self.model = model
        self.question_text = 'Select the class that represents the document the best.'
        self.single_label_cost = self.repetitions * self.price
        self.batch_label_cost = self.batch_size * self.single_label_cost
        self.starting_size = starting_size
        self.verbosity = verbosity

        quals = [Locale(), AcceptRate()]
        self.task = TextClassification(self.client, f'Text Classification - {np.random.randint(100)}', f'{price:.2f}', 'Classify documents into categories', 600, 6000, self.classes, qualifications=quals)

        self.unlabeled = set(range(len(self.data)))
        self.labels = {}

    def _pick_label(self, batch_size):
        assert len(self.unlabeled) >= batch_size
        X_train = self.data[list(self.labels.keys())]
        y_train = list(self.labels.values())
        idx_unlabeled = list(self.unlabeled)
        X_unlabeled = self.data[idx_unlabeled]

        self.model.fit(X_train, y=y_train)
        probs = self.model.predict_proba(X_unlabeled)
        scores = np.apply_along_axis(entropy, 1, probs)
        sorted_idx = np.argsort(-scores)
        return sorted_idx[:batch_size]

    async def _label_doc(self, id_, doc, queue=None):
        answers = []
        async for answer, assignment in self.task.ask_async(verbosity=self.verbosity, assignments=self.repetitions, text=doc, question=self.question_text):
            answers.append(answer)
        # calculate mode
        best_answer = max(set(answers), key=answers.count)
        if queue is not None:
            queue.put_nowait((id_, best_answer))
        
        self.unlabeled.remove(id_)
        self.labels[id_] = best_answer

        return best_answer

    async def label(self, budget):
        queue = asyncio.Queue()
        await self.label_queue(budget, queue)
        return self.labels

    async def label_queue(self, budget, queue):
        random_idx = list(self.unlabeled)
        np.random.shuffle(random_idx)
        random_idx = list(random_idx)

        initial_batch = []
        for _ in range(self.starting_size):
            if not(budget >= self.single_label_cost):
                break
            idx = random_idx.pop()

            initial_batch.append(asyncio.create_task(self._label_doc(idx, self.data[idx], queue=queue)))
            budget -= self.single_label_cost

        await asyncio.gather(*initial_batch)

        while budget >= self.batch_label_cost and len(self.unlabeled) > 0:
            batch_idx = self._pick_label(min(self.batch_size, len(self.unlabeled)))
            al_batch = []
            for idx in batch_idx:
                al_batch.append(asyncio.create_task(self._label_doc(idx, self.data[idx], queue=queue)))
            budget -= self.batch_label_cost

            await asyncio.gather(*al_batch)

def main():
    newsgroups = fetch_20newsgroups()
    model = Pipeline([('tfidf', TfidfVectorizer()), ('logistic', LogisticRegression())])
    al = ActiveLearner(newsgroups.data, newsgroups.target_names, model, repetitions=1, batch_size=1, starting_size=2, verbosity=100)

    print(asyncio.run(al.label(2)))

if __name__ == '__main__':
    main()
