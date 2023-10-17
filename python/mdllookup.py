from typing import Dict, List
import mdlfunction as fun
import pandas as pd


class Lookup:
    def __init__(self, col_type: type = int):
        self.nts_dtype = col_type
        # main mode - trip & stage table
        self.mmd_11id = {
            'swak': {1: 'walk, less than 1 mile'},
            'walk': {2: 'walk, 1 mile or more'},
            'bike': {3: 'bicycle'},
            'car_d': {5: 'private car: driver', 7: 'motorcycle / scooter / moped: driver',
                      11: 'other private transport'},
            'car_p': {6: 'private car: passenger', 8: 'motorcycle / scooter / moped: passenger',
                      20: 'taxi', 21: 'minicab'},
            'van_d': {9: 'van / lorry: driver'},
            'van_p': {10: 'van / lorry: passenger'},
            'bus_d': {},
            'bus_p': {4: 'private (hire) bus', 12: 'london stage bus', 13: 'other stage bus',
                      14: 'coach / express bus', 15: 'excursion / tour bus', 22: 'other public transport'},
            'rail_l': {16: 'london underground', 18: 'light rail'},
            'rail_s': {17: 'surface rail'},
            'air': {19: 'air'},
            'na': {23: 'na (public)', 24: 'na (private)', 25: 'na', -8: 'na', 0: '0'}
        }

        # trip purpose
        self.tpp_01id = {
            'com': {1: 'work', 18: 'escort work'},
            'emb': {2: 'in course of work', 19: 'escort in course of work'},
            'edu': {3: 'education', 20: 'escort education'},
            'shp': {4: 'food shopping', 5: 'non food shopping', 21: 'escort shopping / personal business'},
            'peb': {6: 'personal business medical', 7: 'personal business eat / drink', 8: 'personal business other'},
            'soc': {9: 'eat / drink with friends', 11: 'other social', 12: 'entertain /  public activity',
                    13: 'sport: participate', },  # 16: 'other non-escort', 22: 'other escort'
            'vis': {10: 'visit friends'},  # 17: 'escort home'
            'hol': {14: 'holiday: base'},
            'jwk': {15: 'day trip / just walk'},
            'esc': {17: 'escort home', 16: 'other non-escort', 22: 'other escort'},
            'hom': {23: 'home'}
        }
        # trip purpose included in analysis
        self.inc_purp = [val for key in self.tpp_01id for val in self.tpp_01id[key] if key not in ['hom', 'esc']]

        # weekday & weekend
        self.wkd_01id = {
            'wkd': {1: 'monday', 2: 'tuesday', 3: 'wednesday', 4: 'thursday', 5: 'friday'},
            'sat': {6: 'saturday'},
            'sun': {7: 'sunday'}
        }

        # hours to periods
        self.ttp_01id = {
            'am': {8: '0700 - 0759', 9: '0800 - 0859', 10: '0900 - 0959'},
            'ip': {11: '1000 - 1059', 12: '1100 - 1159', 13: '1200 - 1259',
                   14: '1300 - 1359', 15: '1400 - 1459', 16: '1500 - 1559'},
            'pm': {17: '1600 - 1659', 18: '1700 - 1759', 19: '1800 - 1859'},
            'op': {1: '0000 - 0059', 2: '0100 - 0159', 3: '0200 - 0259', 4: '0300 - 0359',
                   5: '0400 - 0459', 6: '0500 - 0559', 7: '0600 - 0659',
                   20: '1900 - 1959', 21: '2000 - 2059', 22: '2100 - 2159', 23: '2200 - 2259', 24: '2300 - 2359'},
            'na': {-8: 'na', -10: 'dead', 0: '0', '0': '0'}
        }

        # age profile
        self.age_01id = {
            'child': {1: 'less than 1 year', 2: '1 - 2 years', 3: '3 - 4 years',
                      4: '5 - 10 years', 5: '11 - 15 years'},
            'adult': {6: '16 years', 7: '17 years', 8: '18 years', 9: '19 years', 10: '20 years',
                      11: '21 - 25 years', 12: '26 - 29 years', 13: '30 - 39 years', 14: '40 - 49 years',
                      15: '50 - 59 years', 16: '60 - 64 years', 17: '65 - 69 years', 18: '70 - 74 years'},
            'elder': {19: '75 - 79 years', 20: '80 - 84 years', 21: '85 years +'}
        }

        # gender
        self.sex_01id = {
            'male': {1: 'male'},
            'female': {2: 'female'}
        }
        # work status
        self.eco_01id = {
            'fte': {1: 'employees: full-time', 3: 'self-employed: full-time'},
            'pte': {2: 'employees: part-time', 4: 'self-employed: part-time'},
            'stu': {7: 'economically inactive: student'},
            'unm': {5: 'ILO unemployed', 6: 'economically inactive: retired',
                    8: 'economically inactive: looking after family / home',
                    9: 'economically inactive: permanently sick / disabled',
                    10: 'economically inactive: temporarily sick / injured',
                    11: 'economically inactive: other'},
            'dna': {-8: 'na', -9: 'dna', -10: 'dead', 0: '0'}
        }

        # standard occupational classification (individual)
        self.soc_02id = {
            'hig': {1: 'managers and senior officials', 2: 'professional occupations',
                    3: 'associate professional and technical occupations'},
            'med': {4: 'administrative and secretarial occupations', 5: 'skilled trades occupations',
                    6: 'personal service occupations', 7: 'sales and customer service occupations'},
            'low': {8: 'process, plant and machine operatives', 9: 'elementary occupations'},
            'dna': {-8: 'na', -9: 'dna'}
        }

        # national statistics - social economic classification (individual)
        self.sec_03id = {
            'ns1': {1: 'managerial and professional occupations'},
            'ns2': {2: 'intermediate occupations and small employers'},
            'ns3': {3: 'routine and manual occupations'},
            'ns4': {4: 'never worked and long-term unemployed'},
            'ns5': {5: 'not classified (including students)'},
            'dna': {-9: 'dna'}
        }

        # individual income 2002
        self.i02_01id = {
            500: {1: 'Less than £1,000'},
            1500: {2: '£1,000 - £1,999'},
            2500: {3: '£2,000 - £2,999'},
            3500: {4: '£3,000 - £3,999'},
            4500: {5: '£4,000 - £4,999'},
            5500: {6: '£5,000 - £5,999'},
            6500: {7: '£6,000 - £6,999'},
            7500: {8: '£7,000 - £7,999'},
            8500: {9: '£8,000 - £8,999'},
            9500: {10: '£9,000 - £9,999'},
            11250: {11: '£10,000 - £12,499'},
            13750: {12: '£12,500 - £14,999'},
            16250: {13: '£15,000 - £17,499'},
            18750: {14: '£17,500 - £19,999'},
            22500: {15: '£20,000 - £24,999'},
            27500: {16: '£25,000 - £29,999'},
            32500: {17: '£30,000 - £34,999'},
            37500: {18: '£35,000 - £39,999'},
            45000: {19: '£40,000 - £49,999'},
            55000: {20: '£50,000 - £59,999'},
            65000: {21: '£60,000 - £69,999'},
            72500: {22: '£70,000 - £74,999'},
            87500: {23: '£75,000 to £99,999'},
            112500: {24: '£100,000 to £124,999'},
            137500: {25: '£125,000 to £149,999'},
            150000: {26: '£150,000 or more'},
            -1: {-8: 'NA', 0: 'NA'},
            0: {-9: 'DNA (under 16)'}
        }

        # income HHIncome2002_B02ID
        self.i02_02id = {
            1: {key: key for key in range(1, 16)},  # Less than £25,000
            2: {key: key for key in range(16, 20)},  # £25,000 to £49,999
            3: {key: key for key in range(20, 28)},  # £50,000 and over
            0: {-8: 'NA', 0: 'NA'}
        }

        # household reference person
        self.hrp_01id = {
            1: {99: 'Household reference person'},
            0: {1: '', 2: '', 3: '', 4: '', 5: '', 6: '', 7: '', 8: ''}
        }

        # SIC1992 codes
        self.s92_02id = {
            'e13': {1: 'A - Agriculture, hunting and forestry', 2: 'B - Fishing'},
            'e10': {3: 'C - Mining and quarrying', 4: 'D - Manufacturing',
                    5: 'E - Electricity, gas and water supply', 6: 'F - Construction'},
            'e07/09/10': {7: 'G - Wholesale and retail trade; repair of motor vehicles, '
                             'motorcycles and personal and household goods'},
            'e06/07/11': {8: 'H - Hotels and restaurants'},
            'e09/10/12/14': {9: 'I - Transport, storage and communication'},
            'e09/14': {10: 'J - Financial intermediation'},
            'e09/12/14': {11: 'K - Real estate, renting and business activities'},
            'e14': {12: 'L - Public administration and defence; compulsory social security',
                    16: 'P - Private households with employed persons',
                    17: 'Q - Extra-territorial organisations and bodies',
                    18: 'Workplace outside UK (Pre 2002)'},
            'e03/04/05': {13: 'M - Education'},
            'e08/09': {14: 'N - Health and social work'},
            'e12/14': {15: 'O - Other community, social and personal service activities'},
            'na': {-8: 'na'},
            'child': {-9: 'dna'}
        }

        # SIC2007 codes
        self.s07_02id = {
            'e13': {1: 'A - Agriculture, forestry and fishing'},
            'e10': {2: 'B - Mining and quarrying', 3: 'C - Manufacturing',
                    4: 'D - Electricity, gas, steam and air conditioning supply',
                    5: 'E - Water supply; sewerage, waste management and remediation activities',
                    6: 'F - Construction'},
            'e07/09/10': {7: 'G - Wholesale and retail trade; repair of motor vehicles and motorcycles'},
            'e09/10/12/14': {8: 'H - Transportation and storage',
                             10: 'J - Information and communication'},
            'e06/07/11': {9: 'I - Accommodation and food service activities'},
            'e09/14': {11: 'K - Financial and insurance activities'},
            'e09/12/14': {12: 'L - Real estate activities',
                          13: 'M - Professional, scientific and technical activities',
                          14: 'N - Administrative and support service activities'},
            'e14': {15: 'O - Public administration and defence; compulsory social security',
                    20: 'T - Activities of households as employers',
                    21: 'U - Activities of extraterritorial organisations and bodies'},
            'e03/04/05': {16: 'P - Education'},
            'e08/09': {17: 'Q - Human health and social work activities'},
            'e12/14': {18: 'R - Arts, entertainment and recreation', 19: 'S - Other service activities'},
            'na': {-8: 'na'},
            'child': {-9: 'dna'}
        }

        # settlement ruc 2011
        self.set_01id = {
            'major': {'a1': 'urban - major conurbation'},
            'minor': {'b1': 'urban - minor conurbation', '1': 'large urban area - scotland'},
            'city': {'c1': 'urban - city and town', 'c2': 'urban - city and town in a sparse setting',
                     '2': 'other urban area - scotland'},
            'town': {'d1': 'rural - town and fringe', 'd2': 'rural - town and fringe in a sparse setting',
                     '3': 'accessible small town - scotland', '4': 'remote small town - scotland',
                     '5': 'very remote small town - scotland'},
            'village': {'e1': 'rural - village', 'e2': 'rural - village in a sparse setting',
                        'f1': 'rural - hamlets and isolated dwellings',
                        'f2': 'rural - hamlets and isolated dwellings in a sparse setting',
                        '6': 'accessible rural area - scotland', '7': 'remote rural area - scotland',
                        '8': 'very remote rural area - scotland'}
        }

        # ntem area type2
        self.at2_01id = {
            1: {1: 'inner london'},
            2: {2: 'outer london built-up areas'},
            3: {3: 'west midlands built-up areas', 4: 'greater manchester built-up areas',
                5: 'west yorkshire built-up areas', 6: 'glasgow built-up areas', 7: 'liverpool built-up areas',
                8: 'tyneside built-up areas', 9: 'south yorkshire built-up areas'},
            4: {10: 'other urban areas - over 250k population'},
            5: {11: 'other urban areas - 100k to 250k population'},
            6: {12: 'other urban areas - 50k to 100k population', 13: 'other urban areas - 25k to 50k population'},
            7: {14: 'other urban areas - 10k to 25k population', 15: 'other urban areas - 3k to 10k population'},
            8: {16: 'rural'},
            0: {-8: 'na', -9: 'dna', -10: 'dna'}
        }

        # government office region
        self.gor_02id = {1: 'north east', 2: 'north west', 3: 'yorkshire and the humber',
                         4: 'east midlands', 5: 'west midlands', 6: 'east of england',
                         7: 'london', 8: 'south east', 9: 'south west',
                         10: 'wales', 11: 'scotland', -8: 'na', -9: 'dna'
                         }

        # convert specs to either key or values
        self.set_01id = self.dct_to_specs(self.set_01id, col_type)
        self.mmd_11id = self.dct_to_specs(self.mmd_11id, col_type)
        self.tpp_01id = self.dct_to_specs(self.tpp_01id, col_type)
        self.age_01id = self.dct_to_specs(self.age_01id, col_type)
        self.sex_01id = self.dct_to_specs(self.sex_01id, col_type)
        self.eco_01id = self.dct_to_specs(self.eco_01id, col_type)
        self.wkd_01id = self.dct_to_specs(self.wkd_01id, col_type)
        self.ttp_01id = self.dct_to_specs(self.ttp_01id, col_type)
        self.soc_02id = self.dct_to_specs(self.soc_02id, col_type)
        self.sec_03id = self.dct_to_specs(self.sec_03id, col_type)
        self.at2_01id = self.dct_to_specs(self.at2_01id, col_type)
        self.i02_01id = self.dct_to_specs(self.i02_01id, col_type)
        self.i02_02id = self.dct_to_specs(self.i02_02id, col_type)
        self.hrp_01id = self.dct_to_specs(self.hrp_01id, col_type)
        self.s07_02id = self.dct_to_specs(self.s07_02id, col_type)
        self.s92_02id = self.dct_to_specs(self.s92_02id, col_type)

    def gender(self) -> Dict:
        # gender
        age_01id, sex_01id = self.age_01id, self.sex_01id
        out_dict = {'col': ['sex_b01id', 'age_b01id'],
                    'typ': [self.nts_dtype, self.nts_dtype],
                    'log': 'gender',
                    'val': {1: fun.product(sex_01id['male'] + sex_01id['female'], age_01id['child']),  # child
                            2: fun.product(sex_01id['male'], age_01id['adult'] + age_01id['elder']),  # male
                            3: fun.product(sex_01id['female'], age_01id['adult'] + age_01id['elder'])  # female
                            },
                    'out': {1: 'child', 2: 'male', 3: 'female'}  # for output
                    }
        out_dict['val'] = self.val_to_key(out_dict['val'])
        return out_dict

    def hh_type(self) -> Dict:
        # household type
        out_dict = {'col': ['hholdnumadults', 'numcarvan'],
                    'typ': [int, int],
                    'log': 'hh_type',
                    'val': {1: [(1, 0)],  # 1 adult with 0 car
                            2: fun.product([1], range(1, 10)),  # 1 adult with 1+ cars
                            3: [(2, 0)],  # 2 adults with 0 car
                            4: [(2, 1)],  # 2 adults with 1 car
                            5: fun.product([2], range(2, 10)),  # 2 adults with 2+ cars
                            6: fun.product(range(3, 11), [0]),  # 3+ adults with 0 car
                            7: fun.product(range(3, 11), [1]),  # 3+ adults with 1 car
                            8: fun.product(range(3, 11), range(2, 10))  # 3+ adults with 2+ cars
                            },
                    'out': {1: '1 adult with 0 car', 2: '1 adult with 1+ cars', 3: '2 adults with 0 car',
                            4: '2 adults with 1 car', 5: '2 adults with 2+ cars', 6: '3+ adults with 0 car',
                            7: '3+ adults with 1 car', 8: '3+ adults with 2+ cars'}
                    }
        out_dict['val'] = self.val_to_key(out_dict['val'])
        return out_dict

    def aws(self) -> Dict:
        # age, work, status
        eco_01id, age_01id = self.eco_01id, self.age_01id
        eco_over = eco_01id['fte'] + eco_01id['pte'] + eco_01id['unm'] + eco_01id['dna']
        out_dict = {'col': ['age_b01id', 'ecostat_b01id'],
                    'typ': [self.nts_dtype, self.nts_dtype],
                    'log': 'aws',
                    'val': {1: fun.product(age_01id['child'], eco_01id['dna']),  # child
                            2: fun.product(age_01id['adult'], eco_01id['fte']),  # fte
                            3: fun.product(age_01id['adult'], eco_01id['pte']),  # pte
                            4: fun.product(age_01id['adult'] + age_01id['elder'], eco_01id['stu']),  # student
                            5: fun.product(age_01id['adult'], eco_01id['unm']),  # unemployed
                            6: fun.product(age_01id['elder'], eco_over),  # over 75
                            },
                    'out': {1: 'child', 2: 'fte', 3: 'pte', 4: 'student', 5: 'neet', 6: 'over 75'}
                    }
        out_dict['val'] = self.val_to_key(out_dict['val'])
        return out_dict

    def soc(self) -> Dict:
        # soc
        soc_02id, age_01id, eco_01id = self.soc_02id, self.age_01id, self.eco_01id
        all_xsoc = soc_02id['hig'] + soc_02id['med'] + soc_02id['low'] + soc_02id['dna']
        all_ages = age_01id['child'] + age_01id['adult'] + age_01id['elder']
        emp_ecos = eco_01id['fte'] + eco_01id['pte']
        all_ecos = emp_ecos + eco_01id['stu'] + eco_01id['unm'] + eco_01id['dna']
        out_dict = {'col': ['xsoc2000_b02id', 'age_b01id', 'ecostat_b01id'],
                    'typ': [self.nts_dtype, self.nts_dtype, self.nts_dtype],
                    'log': 'soc',
                    'val': {1: fun.product(soc_02id['hig'], age_01id['adult'], emp_ecos),  # high skill
                            2: fun.product(soc_02id['med'], age_01id['adult'], emp_ecos),  # med skill
                            3: fun.product(soc_02id['low'], age_01id['adult'], emp_ecos),  # low skill
                            4: (fun.product(all_xsoc, all_ages, eco_01id['stu']) +  # student
                                fun.product(all_xsoc, age_01id['adult'], eco_01id['unm']) +  # unemployed
                                fun.product(all_xsoc, age_01id['child'], all_ecos) +  # children
                                fun.product(all_xsoc, age_01id['elder'], all_ecos)),  # over 75
                            #  0: fun.product(soc_02id['dna'], age_01id['adult'], emp_ecos)  # other
                            },
                    'out': {1: '1. high skilled', 2: '2. medium skilled', 3: '3. low skilled', 4: '4. other'}
                    }
        out_dict['val'] = self.val_to_key(out_dict['val'])
        return out_dict

    def ns_sec(self) -> Dict:
        # ns-sec
        out_dict = {'col': 'nssec_b03id', 'typ': self.nts_dtype, 'log': 'ns-sec',
                    'val': {1: self.sec_03id['ns1'],  # manager & professional
                            2: self.sec_03id['ns2'],  # intermediate
                            3: self.sec_03id['ns3'],  # manual & routine
                            4: self.sec_03id['ns4'],  # unemployed
                            5: self.sec_03id['ns5'] + self.sec_03id['dna'],  # not classified + students
                            },
                    'out': {1: '1. manager & professional', 2: '2. intermediate & small employers',
                            3: '3. routine & manual', 4: '4. unemployed', 5: '5. not classified (inc. students)'}
                    }
        out_dict['val'] = self.val_to_key(out_dict['val'])
        return out_dict

    def hrp(self) -> Dict:
        # hrp
        out_dict = {'col': 'hrprelation_b01id', 'typ': self.nts_dtype, 'log': 'hrp',
                    'val': {1: self.hrp_01id[1]},
                    'out': {1: 'household reference person', 0: 'other'}
                    }
        out_dict['val'] = self.val_to_key(out_dict['val'])
        return out_dict

    def income(self, col_name: str, lev_name: str = '01') -> Dict:
        # household or individual income: {ind/hh}income2002_b{01/02}id
        col_name = f'{col_name}income2002_b01id'
        out_dict = {'col': col_name, 'typ': self.nts_dtype, 'log': 'income',
                    'val': eval(f'self.i02_{lev_name}id')}
        out_dict['val'] = self.val_to_key(out_dict['val'])
        return out_dict

    def sic(self, sic_year: str = '2007') -> Dict:
        out_dict = {'col': f'sic{sic_year}_b02id', 'typ': self.nts_dtype, 'log': f'sic{sic_year}',
                    'val': eval(f'self.s{sic_year[2:]}_02id')}
        out_dict['val'] = self.val_to_key(out_dict['val'])
        return out_dict

    def tt_tfn(self, col_list: List, out_type: str = 'tfn') -> Dict:
        # tfn traveller type
        def _dct_value(idx: int) -> List:
            try:
                key = col_list[idx]
                return list(set(par_dict[key]['val'].values()))
            except IndexError:
                return [None, None, None, None]

        def _dct_update(*args) -> Dict:
            args = (fun.str_to_list(col) for col in args)
            args = (col for col in args if all(itm is not None for itm in col))
            if len(par_dict) == 0:
                return {idx: val for idx, val in enumerate(fun.product(*args), 1)}
            else:
                idx_init = len(par_dict) + 1
                par_dict.update({idx: val for idx, val in enumerate(fun.product(*args), idx_init)})
                return par_dict

        # tt = [gender, aws, hh_type, soc, ns]
        par_dict = {'gender': self.gender(), 'aws': self.aws(), 'hh_type': self.hh_type(),
                    'soc': self.soc(), 'ns': self.ns_sec()}
        gen, aws, hh = _dct_value(0), _dct_value(1), _dct_value(2)
        soc, sec = _dct_value(3), _dct_value(4)

        # child: gender=1, aws=1, hh=1-8, soc=4, ns=1-5
        par_dict = {}
        par_dict = _dct_update(gen[0], aws[0], hh, soc[-1], sec)
        if out_type == 'tfn':
            for g in gen[1:]:
                # fte/pte: gender=2-3, aws=2-3, (hh=1-2, soc=1-3, ns=1-3,5) & (hh=3-8, soc=1-3, ns=1-5)
                par_dict = _dct_update(g, 2, hh[:2], [1, 2], [1, 2, 3, 5])
                par_dict = _dct_update(g, 2, hh[:2], 3, [2, 3, 5])
                par_dict = _dct_update(g, 2, hh[2:], [1, 2, 3], sec)
                par_dict = _dct_update(g, 3, hh[:2], [1, 2], [1, 2, 3, 5])
                par_dict = _dct_update(g, 3, hh[:2], 3, [2, 3, 5])
                par_dict = _dct_update(g, 3, hh[2:], [1, 2, 3], sec)
                # student: gender=2-3, aws=4, (hh=1-2, soc=4, ns=5) & (hh=3-8, soc=4, ns=1-5)
                par_dict = _dct_update(g, 4, hh[:2], 4, 5)
                par_dict = _dct_update(g, 4, hh[2:], 4, sec)
                # unemployed: gender=2-3, aws=5, (hh=1-8, soc=4, ns=1-5)
                par_dict = _dct_update(g, 5, hh, 4, sec)
                # over 75 gender=2-3, aws=6, hh=1-8, soc=4, ns=1-5
                par_dict = _dct_update(g, 6, hh, 4, sec)
        else:
            # fte/pte: gender=2-3, aws=2-6, hh=1-8
            par_dict = _dct_update(gen[1:], aws[1:], hh)

        return self.val_to_key(par_dict)

    def tt_to_dfr(self, tfn_type: List, out_type: str = 'tfn') -> pd.DataFrame:
        dfr = self.tt_tfn(tfn_type, out_type)
        dfr = pd.DataFrame.from_dict({val: key for key, val in dfr.items()}, orient='index')
        dfr.rename(columns={key: val for key, val in enumerate(tfn_type)}, inplace=True)
        dfr = dfr.reset_index(drop=False).rename(columns={'index': 'tt'})
        return dfr

    def at_ntem(self, col_name: str) -> Dict:
        # ntem area type
        out_dict = {'col': f'{col_name}areatype_b01id', 'typ': self.nts_dtype, 'log': 'ntem_at',
                    'val': self.at2_01id,
                    'out': {1: 'inner london', 2: 'outer london', 3: 'metropolitan', 4: 'urban big',
                            5: 'urban large', 6: 'urban medium', 7: 'urban small', 8: 'rural'}
                    }
        out_dict['val'] = self.val_to_key(out_dict['val'])
        return out_dict

    def at_tfn(self, col_type: str) -> Dict:
        # test new area types that based on ruc, ntem & gor
        # col_type: hhold, triporig, tripdest
        # 1: 'north east', 2: 'north west', 3: 'yorkshire and the humber', 4: 'east midlands',
        # 5: 'west midlands', 6: 'east of england', 7: 'london', 8: 'south east', 9: 'south west',
        # 10: 'wales', 11: 'scotland', -8: 'na', -9: 'dna'
        set_01id, at2_01id = self.set_01id, self.at2_01id
        all_cnty = [-8, -9] + list(range(10, 89))
        set_list = [val for key in set_01id for val in set_01id[key]]
        non_ldon = [val for key in at2_01id for val in at2_01id[key] if val not in at2_01id[1] + at2_01id[2]]
        out_ldon = [val for key in at2_01id for val in at2_01id[key] if val not in at2_01id[1]]
        enw_list = [1, 2, 3, 4, 5, 6, 8, 9, 10]  # england & wales only, exc. london
        out_dict = {'col': [f'{col_type}gor_b02id', f'{col_type}county_b01id', f'{col_type}areatype_b01id',
                            f'{col_type}ruc2011_b01id'],
                    'typ': [self.nts_dtype, self.nts_dtype, self.nts_dtype, str],
                    'log': f'tfn_at ({col_type})',
                    'val': {1: fun.product([7], all_cnty, at2_01id[1], set_list),  # inner london
                            2: (fun.product([7], all_cnty, out_ldon, set_list) +  # outer london within london
                                fun.product([6, 8], all_cnty, at2_01id[2], set_list)),  # outer london outside london
                            3: (fun.product([1, 3], all_cnty, non_ldon, set_01id['major']) +  # major (ne + yh)
                                fun.product([1, 3], all_cnty, non_ldon, set_01id['minor'])),  # minor (yh)
                            4: fun.product([2, 4], all_cnty, non_ldon, set_01id['major']),  # major (nw + em)
                            5: fun.product([5], all_cnty, non_ldon, set_01id['major']),  # major (wm)
                            6: fun.product([1, 3], all_cnty, non_ldon, set_01id['city']),  # city (ne + yh)
                            7: (fun.product([2], all_cnty, non_ldon, set_01id['city']) +  # city (nw)
                                fun.product([10], [60, 63], non_ldon, set_01id['city'])),  # city (wales)
                            8: fun.product([4], all_cnty, non_ldon, set_01id['minor'] + set_01id['city']),  # city (em)
                            9: (fun.product([5], all_cnty, non_ldon, set_01id['city']) +  # city (wm)
                                fun.product([10], [61, 65], non_ldon, set_01id['city'])),  # city (wales)
                            10: fun.product([6], all_cnty, non_ldon, set_01id['major'] + set_01id['city']),  # city (east)
                            11: fun.product([8], all_cnty, non_ldon, set_01id['major'] + set_01id['city']),  # city (se)
                            12: (fun.product([9], all_cnty, non_ldon, set_01id['city']) +  # city (sw)
                                 fun.product([10], [62, 64, 66, 67], non_ldon, set_01id['city'])),  # city (wales)
                            13: fun.product(enw_list, all_cnty, non_ldon, set_01id['town']),  # town
                            14: fun.product(enw_list, all_cnty, non_ldon, set_01id['village']),  # village
                            15: fun.product([11], all_cnty, non_ldon, set_list),  # scotland
                            },
                    'out': {1: 'inner london', 2: 'outer london', 3: 'major (ne + yh) + minor (yh)',
                            4: 'major (nw + em)', 5: 'major (wm)', 6: 'city (ne + yh)', 7: 'city (nw)',
                            8: 'city + minor (em)', 9: 'city (wm)', 10: 'city (east)', 11: 'city (se)',
                            12: 'city (sw)', 13: 'town', 14: 'village', 15: 'scotland'}
                    }
        out_dict['val'] = self.val_to_key(out_dict['val'])
        return out_dict

    def at_tfn_v1(self, col_type: str) -> Dict:
        # test new area types that based on ruc, ntem & gor
        # col_type: hhold, triporig, tripdest
        # 1: 'north east', 2: 'north west', 3: 'yorkshire and the humber', 4: 'east midlands',
        # 5: 'west midlands', 6: 'east of england', 7: 'london', 8: 'south east', 9: 'south west',
        # 10: 'wales', 11: 'scotland', -8: 'na', -9: 'dna'
        set_01id, at2_01id = self.set_01id, self.at2_01id
        set_list = [val for key in set_01id for val in set_01id[key]]
        non_ldon = [val for key in at2_01id for val in at2_01id[key] if val not in at2_01id[1] + at2_01id[2]]
        out_ldon = [val for key in at2_01id for val in at2_01id[key] if val not in at2_01id[1]]
        enw_list = [1, 2, 3, 4, 5, 6, 8, 9]  # england only, exc. london
        out_dict = {'col': [f'{col_type}gor_b02id', f'{col_type}areatype_b01id', f'{col_type}ruc2011_b01id'],
                    'typ': [self.nts_dtype, self.nts_dtype, str],
                    'log': f'tfn_at ({col_type})',
                    'val': {1: fun.product([7], at2_01id[1], set_list),  # inner london
                            2: (fun.product([7], out_ldon, set_list) +  # outer london + major (east, se)
                                fun.product([6, 8], at2_01id[2], set_list)),
                            3: fun.product([1, 3], non_ldon, set_01id['major']),  # major (ne + yh)
                            4: fun.product([2, 4], non_ldon, set_01id['major']),  # major (nw + em)
                            5: fun.product([5], non_ldon, set_01id['major']),  # major (wm)
                            6: fun.product(enw_list, non_ldon, set_01id['minor']),  # minor
                            7: fun.product([1, 3], non_ldon, set_01id['city']),  # city (ne + yh)
                            8: fun.product([2], non_ldon, set_01id['city']),  # city (nw)
                            9: fun.product([4], non_ldon, set_01id['city']),  # city (em)
                            10: fun.product([5], non_ldon, set_01id['city']),  # city (wm)
                            11: fun.product([6], non_ldon, set_01id['major'] + set_01id['city']),  # city (east)
                            12: fun.product([8], non_ldon, set_01id['major'] + set_01id['city']),  # city (se)
                            13: fun.product([9], non_ldon, set_01id['city']),  # city (sw)
                            14: fun.product(enw_list, non_ldon, set_01id['town']),  # town
                            15: fun.product(enw_list, non_ldon, set_01id['village']),  # village
                            16: fun.product([10], non_ldon, set_list),  # wales
                            17: fun.product([11], non_ldon, set_list),  # scotland
                            },
                    'out': {1: 'inner london', 2: 'outer london', 3: 'major (ne + yh)', 4: 'major (nw + em)',
                            5: 'major (wm)', 6: 'minor (em + yh)', 7: 'city (ne + yh)', 8: 'city (nw)',
                            9: 'city (em)', 10: 'city (wm)', 11: 'city (east)', 12: 'city (se)',
                            13: 'city (sw)', 14: 'town', 15: 'village', 16: 'wales', 17: 'scotland'}
                    }
        out_dict['val'] = self.val_to_key(out_dict['val'])
        return out_dict

    def settlement(self, col_type: str) -> Dict:
        # ruc 2011 to area type
        out_dict = {'col': f'{col_type}ruc2011_b01id',
                    'typ': str,
                    'log': f'{col_type}ruc_2011',
                    'val': {1: self.set_01id['major'],
                            2: self.set_01id['minor'],
                            3: self.set_01id['city'],
                            4: self.set_01id['town'],
                            5: self.set_01id['village']
                            },
                    'out': {1: 'major conurbation', 2: 'minor conurbation', 3: 'city & town',
                            4: 'town & fringe', 5: 'village'}
                    }
        out_dict['val'] = self.val_to_key(out_dict['val'])
        return out_dict

    def occupant(self) -> Dict:
        # occupant
        mmd_11id = self.mmd_11id
        out_dict = {'col': ['mainmode_b11id'],
                    'typ': [self.nts_dtype],
                    'log': 'occupancy',
                    'val': {'driver': (mmd_11id['swak'] + mmd_11id['walk'] + mmd_11id['bike'] +
                                       mmd_11id['car_d'] + mmd_11id['van_d'] + mmd_11id['bus_d']),
                            'passenger': (mmd_11id['car_p'] + mmd_11id['van_p'] + mmd_11id['bus_p'] +
                                          mmd_11id['rail_s'] + mmd_11id['rail_l'] + mmd_11id['air'])
                            }
                    }
        out_dict['val'] = self.val_to_key(out_dict['val'])
        return out_dict

    def mode(self, col_mode: str = 'main') -> Dict:
        # main mode
        out_dict = {'col': [f'{col_mode}mode_b11id'],
                    'typ': [self.nts_dtype],
                    'log': f'{col_mode} mode',
                    'val': {1: self.mmd_11id['swak'] + self.mmd_11id['walk'],  # walk
                            2: self.mmd_11id['bike'],  # cycle
                            3: self.mmd_11id['car_d'] + self.mmd_11id['car_p'],  # car driver/passenger
                            4: self.mmd_11id['van_d'] + self.mmd_11id['van_p'],  # van driver/passenger
                            5: self.mmd_11id['bus_d'] + self.mmd_11id['bus_p'],  # bus
                            6: self.mmd_11id['rail_s'],  # surface rail
                            7: self.mmd_11id['rail_l'],  # light rail/underground
                            8: self.mmd_11id['air']  # air
                            },
                    'out': {1: 'walk', 2: 'cycle', 3: 'car', 4: 'van', 5: 'bus', 6: 'surface rail',
                            7: 'light rail', 8: 'air'}
                    }
        out_dict['val'] = self.val_to_key(out_dict['val'])
        return out_dict

    def purpose(self) -> Dict:
        # trip purpose
        tpp_01id, end_home = self.tpp_01id, self.tpp_01id['hom']
        tpp_from = self.inc_purp + self.tpp_01id['esc'] + end_home
        all_mode = [val for key in self.mmd_11id for val in self.mmd_11id[key] if key != 'na']
        non_walk = [val for key in self.mmd_11id for val in self.mmd_11id[key] if key not in ['na', 'swak', 'walk']]
        out_dict = {'col': ['mainmode_b11id', 'trippurpfrom_b01id', 'trippurpto_b01id'],
                    'typ': [self.nts_dtype, self.nts_dtype, self.nts_dtype],
                    'log': 'purpose',
                    'val': {1: (fun.product(all_mode, tpp_from, tpp_01id['com']) +  # from home/non-home base
                                fun.product(all_mode, tpp_01id['com'], end_home)),  # return home
                            2: (fun.product(all_mode, tpp_from, tpp_01id['emb']) +
                                fun.product(all_mode, tpp_01id['emb'], end_home)),
                            3: (fun.product(all_mode, tpp_from, tpp_01id['edu']) +
                                fun.product(all_mode, tpp_01id['edu'], end_home)),
                            4: (fun.product(all_mode, tpp_from, tpp_01id['shp']) +
                                fun.product(all_mode, tpp_01id['shp'], end_home)),
                            5: (fun.product(all_mode, tpp_from, tpp_01id['peb']) +
                                fun.product(all_mode, tpp_01id['peb'], end_home)),
                            6: (fun.product(all_mode, tpp_from, tpp_01id['soc']) +
                                fun.product(all_mode, tpp_01id['soc'], end_home)),
                            7: (fun.product(all_mode, tpp_from, tpp_01id['vis']) +
                                fun.product(all_mode, tpp_01id['vis'], end_home)),
                            8: (fun.product(all_mode, tpp_from, tpp_01id['hol']) +
                                fun.product(all_mode, tpp_01id['hol'], end_home) +
                                fun.product(non_walk, tpp_from, tpp_01id['jwk']) +
                                fun.product(non_walk, tpp_01id['jwk'], end_home))
                            },
                    'out': {1: 'commute', 2: 'employer business', 3: 'education', 4: 'shopping',
                            5: 'personal business', 6: 'social', 7: 'visit friends', 8: 'holiday'}
                    }
        out_dict['val'] = self.val_to_key(out_dict['val'])
        return out_dict

    def period(self, ttp_type: str = 'start') -> Dict:
        # trip start/end time
        wkd_01id, ttp_01id = self.wkd_01id, self.ttp_01id
        all_24hr = ttp_01id['am'] + ttp_01id['ip'] + ttp_01id['pm'] + ttp_01id['op'] + ttp_01id['na']
        out_dict = {'col': ['travelweekday_b01id', f'trip{ttp_type}_b01id'],
                    'typ': [self.nts_dtype, self.nts_dtype],
                    'log': f'{ttp_type} time',
                    'val': {1: fun.product(wkd_01id['wkd'], ttp_01id['am']),
                            2: fun.product(wkd_01id['wkd'], ttp_01id['ip']),
                            3: fun.product(wkd_01id['wkd'], ttp_01id['pm']),
                            4: fun.product(wkd_01id['wkd'], ttp_01id['op']),
                            5: fun.product(wkd_01id['sat'], all_24hr),
                            6: fun.product(wkd_01id['sun'], all_24hr)
                            },
                    'out': {1: 'AM peak', 2: 'Inter-peak', 3: 'PM peak', 4: 'Off-peak', 5: 'Saturday', 6: 'Sunday'}
                    }
        out_dict['val'] = self.val_to_key(out_dict['val'])
        return out_dict

    def direction(self) -> Dict:
        # direction of travel, hb_fr, hb_to, nhb
        nhb_purp = self.inc_purp + self.tpp_01id['esc']
        out_dict = {'col': ['trippurpfrom_b01id', 'trippurpto_b01id'],
                    'typ': [self.nts_dtype, self.nts_dtype],
                    'log': 'direction',
                    'val': {'hb_fr': fun.product(self.tpp_01id['hom'], nhb_purp),
                            'hb_to': fun.product(nhb_purp, self.tpp_01id['hom']),
                            'nhb': fun.product(nhb_purp, nhb_purp)
                            }
                    }
        out_dict['val'] = self.val_to_key(out_dict['val'])
        return out_dict

    @staticmethod
    def val_to_key(dct: Dict) -> Dict:
        dct = {key: [dct[key]] if not isinstance(dct[key], list) else dct[key] for key in dct}
        return {fun.str_lower(val): key for key in dct for val in dct[key]}

    @staticmethod
    def dct_to_specs(dct: Dict, out: type = int) -> Dict:
        return {key: list(dct[key].keys() if out is int else dct[key].values()) for key in dct}

    def agg_type(self, tfn_type: str = 'tfn') -> Dict:
        out_dict = {'at': {1: [], 2: [], 3: [], 4: [], 5: [], 6: []},
                    'hh': {1: [], 2: [], 3: []}
                    }
        out_dict = self.val_to_key(out_dict)
        return out_dict

    @staticmethod
    def fun_aggregate(dfr: pd.DataFrame, col_2agg: List) -> Dict:
        """
        aggregation:
            level 1: p, gen, aws, soc, ns, hh, at
            level 2: p, gen, aws, soc, ns, hh
            level 3: p, gen, aws, soc, ns
            level 4: p, gen, aws, soc
            level 5: p, gen, aws
        if pop[xyz] > 300:
            trip_rate[xyz] = trip[xyz] / pop[xyz]
        elif pop[xyz, (at)] > 300:
            trip_rate[xyz, (at)] =
        elif pop[xyz, (at, hh)] > 300:
            trip_rate[xyz, (at, hh)] =
        elif pop[xyz, (at, hh, ns)] > 300:
            trip_rate[xyz, (at, hh, ns)] =
        elif pop[xyz, (at, hh, ns, soc)] > 300:
            trip_rate[xyz, (at, hh, ns, soc)] =
        else:
            trip_rate[xyz, (at, hh, ns, soc, aws)] =
        """
        out_dict = {'lev1': {}, 'lev2': {}, 'lev3': {}}

        return out_dict