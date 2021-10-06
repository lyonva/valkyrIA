
fftf = {
    "max_depth" : [ "grid", 2, 5, 1 ],
    "score_support" : [ "grid", 1, 4, 1 ],
    "min_samples_split" : [ "grid", 3, 50, 1 ],
    "min_bin_exp" : [ "float", 0.1, 0.9 ],
    "d" : [ "grid", 1, 4, 1 ],
    "cohen" : [ "float", 0.1, 1.5 ],
    "random_proj_exp" : [ "float", 0.3, 0.7 ],
    "random_proj_depth" : [ "grid", 2, 5, 1 ],
    "target" : [ "values", "1" ]
}

fft = {
    "structure" : [ "grid", 1, 31, 1 ],
    "max_depth" : [ "grid", 2, 5, 1 ],
    "score_support" : [ "grid", 1, 4, 1 ],
    "min_samples_split" : [ "grid", 6, 50, 1 ],
    "min_bin_exp" : [ "float", 0.1, 0.9 ],
    "d" : [ "grid", 1, 4, 1 ],
    "cohen" : [ "float", 0.1, 1.5 ],
    "random_proj_exp" : [ "float", 0.3, 0.7 ],
    "random_proj_depth" : [ "grid", 2, 5, 1 ],
    "target" : [ "values", "1" ]
}
