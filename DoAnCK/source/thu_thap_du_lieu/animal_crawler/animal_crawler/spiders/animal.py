import os
from pprint import pprint
from time import sleep
import pandas as pd
import scrapy


def create_dict(keys, values):
    keys = [name.strip().capitalize() for name in keys]
    values = [name.strip() for name in values]
    dictionary = dict(zip(keys, values))
    return dictionary


def split_to_lines(values):
    values = [value for value in values if value not in ['Show More', 'Show Less']]
    joined = ''.join(values)
    lines = [line.replace('\n', '').strip() for line in joined.replace('\n\n\n', '\n\n').split('\n\n')]
    return lines

class AnimalsSpider(scrapy.Spider):
    name = "animals"

    def start_requests(self):
        df = pd.read_csv('../animals_urls.csv')
        list_urls = df[df['url'] != "/grey-wolf"]['url']
        list_urls[:] = 'https://animalia.bio' + list_urls[:]
        yield scrapy.Request(url='https://animalia.bio/grey-wolf', callback=self.parse)
        sleep(2)
        for url in list_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: scrapy.http.TextResponse):
        dict_general_info = {}
        # name of animal
        dict_general_info['Name'] = response.css('.a-h1::text').get().strip()

        # general attribite
        attr_names = response.css('.s-char-kinds__attr::text').getall() + response.css('.s-char-char__name::text').getall()
        elem_names = response.css('.s-char-kinds__name::text').getall() + response.css('.s-char-char__num::text').getall()

        dict_general_info.update(create_dict(attr_names, elem_names))

        dict_general_info['Attributes'] = response.css('.s-char-status-item span::text').getall()
        dict_general_info['Attributes'] = [attr for attr in dict_general_info['Attributes'] if attr != ' (collection)']

        # distribution 
            # geography
        geo_values = response.css('.s-distr-block--row .col-sm-9 *::text').getall()
        geography = create_dict(response.css('.s-distr-geography__slug::text').getall(), split_to_lines(geo_values))

            # biome
        biome = response.css('.s-distr-zone-item span::text').getall()

            # climate zone
        climate = response.css('.s-distr-climate__link span::text').getall()
            # aggregation
        dict_general_info['Distribution'] = {'Geography': geography, 'Biome': biome,
                                             'Climate': climate}

        # habit and lifestyle
        habit_keys = response.css('.s-habbit-group__slug::text').getall()
        habit_values = response.css('.s-habbit-group .col-sm-9 *::text').getall()
        dict_general_info['Habits'] = create_dict(habit_keys, split_to_lines(habit_values))

        # Diet
        dict_general_info['Diet'] = [diet.strip() for diet in response.css('.s-diet-item__link::text').getall()]

        # Mating Habits
        mating_keys = response.css('.s-mating-slug__text::text').getall()
        mating_values = response.css('.s-mating-char :nth-child(1)::text').getall()
        dict_general_info['Mating_Habits'] = create_dict(mating_keys, mating_values)


        # population
        population_keys = response.css('.s-population-slug::text').getall()
        population_values = response.css('.s-population__link::text').getall()
        dict_general_info['Population'] = create_dict(population_keys, population_values)



        # print('============================================================================')
        # print('============================================================================')
        # print('============================================================================')
        # print('============================================================================')
        # pprint(dict_general_info)
        # print('============================================================================\n\n\n')
        return dict_general_info
        
