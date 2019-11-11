from pathlib import Path
from typing import Optional
import yaml

class Locale(object):
    def __init__(self, country: str='US'):
        self.country = country

    def get(self):
        return {
            'QualificationTypeId': '00000000000000000071',
            'Comparator': 'EqualTo',
            'LocaleValues': [
                {
                    'Country': self.country,
                },
            ],
            'ActionsGuarded': 'DiscoverPreviewAndAccept',
        }

class AcceptRate(object):
    def __init__(self, percentage: int=90):
        self.percentage = percentage

    def get(self):
        return {
            'QualificationTypeId': '000000000000000000L0',
            'Comparator': 'GreaterThan',
            'IntegerValues': [
                self.percentage,
            ],
            'ActionsGuarded': 'DiscoverPreviewAndAccept',
        }

class Unique(object):
    def __init__(self, mturk_client, unique_id: str, description: str='', cache: str=False, cache_path: Optional[str]=None):
        self.mturk_client = mturk_client
        self.unique_id = unique_id
        self.description = description
        if cache:
            self.run_id = 'universe'
            if cache_path is None:
                base_path = Path.cwd() / '.turkit_cache'
            else:
                base_path = Path(cache_path)

            if not base_path.exists():
                os.mkdir(str(base_path))

            self.cache_path = base_path / f'{self.run_id}.yaml'

        self.qual = None

    def _create_unique_qualification(self):
        response = self.mturk_client.create_qualification_type(
            Name=self.unique_id,
            Description=f'This qualification is for workers who have on this task before- {self.description}',
            QualificationTypeStatus='Active',
            AutoGranted=True,
        )

        return str(response['QualificationType']['QualificationTypeId'])

    def get(self):
        if self.qual is not None:
            return self.qual

        cache = self._get_cache()
        cache.setdefault('unique_qual', {})
        if self.unique_id in cache['unique_qual']:
            self.qual = cache['unique_qual'][self.unique_id]
            return self.qual
        else:
            qual_id = self._create_unique_qualification()
            self.qual = {
                'QualificationTypeId': qual_id,
                'Comparator': 'DoesNotExist'
            }
            cache['unique_qual'][self.unique_id] = self.qual
            self._write_cache(cache)
            return self.qual

    def _get_cache(self):
        if not self.cache_path.exists():
            return dict()
        with self.cache_path.open('r') as f:
            result = yaml.load(f, Loader=yaml.BaseLoader)
            if result is None:
                return dict()
            else:
                return result

    def _write_cache(self, new_cache):
        with self.cache_path.open('w') as f:
            yaml.dump(new_cache, f)
