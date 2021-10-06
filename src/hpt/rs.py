from random import choice, uniform

class RandomSearch:

    def __init__(self, n_iter = 60):
        self.n_iter = n_iter
    
    def fit(self, model, df, search_space):
        return [ self.one_credit(model, df, search_space) for i in range(self.n_iter) ]

    def one_credit(self, model, df, search_space):
        hyper_params = { key : self.random_hyperparam( val ) for key, val in search_space.items() }
        return model(df, **hyper_params)
    
    def random_hyperparam( self, hp_range ):
        r_type = hp_range[0]
        if r_type == "grid":
            init = 0
            end = 0
            incr = 1
            if len(hp_range) == 2:
                end = hp_range[1]
            if len(hp_range) >= 3:
                init = hp_range[1]
                end = hp_range[2]
            if len(hp_range) >= 4:
                incr = hp_range[3]
            
            # Create all posibilities
            values = []
            i = init
            while i <= end:
                values.append(i)
                i += incr
            
            return choice(values)

        elif r_type == "float":
            a, b = hp_range[1], hp_range[2]
            return uniform(a, b)
        else:
            return None

