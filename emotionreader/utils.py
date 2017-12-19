def chunks(l, n):
    """
    Yield `n` sized chunks from iterable `l`.
    """
    for i in range(0, len(l), n):
        yield l[i:i+n]


def average_emotions(iterable, chunk_size=5):
    """ Get the average of 5 frames on emotion predictions.

    The video emotion predictor return a list of all 8 emotions
    for each processed frame. This function takes the average
    emotion for each 5 frames of predictions.

    Arguments:
        :param iterable: the list of lists with emotions
    """
    if len(iterable) == 0:
        raise ValueError('no values in list to combine')
    if len(iterable) == 1:
        # only one item in list, no need to combine
        return iterable[0]

    result = []
    for frame_chunk in chunks(iterable, chunk_size):
        divnum = chunk_size
        # there are 8 emotions. Without filling them like this
        # we would get index out of range in avg[i] = emotion
        avg = [0 for x in range(8)]
        for prediction in frame_chunk:
            if prediction is None:
                divnum -= 1
                continue
            for i, emotion in enumerate(prediction):
                avg[i] += emotion
        if divnum == 0:
            result.append(None)
        else:
            result.append([x / divnum for x in avg])
    return result
