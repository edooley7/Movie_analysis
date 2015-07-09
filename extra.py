__author__ = 'erindooley'
def runtime_to_minutes(runtimestring):
    runtime = runtimestring.split()
    try:
        minutes = int(runtime[0])*60 + int(runtime[2])
        return minutes
    except:
        return None

def to_date(datestring):
    date = dateutil.parser.parse(datestring)
    return date

genre = get_movie_values(soup,'Genre')
print "Genre:", genre

raw_runtime = get_movie_values(soup,'Runtime')
runtime = runtime_to_minutes(raw_runtime)
print "Runtime:", runtime

rating = get_movie_values(soup,'MPAA Rating')
print "Rating:", rating

studio = get_movie_values(soup,'Studio')
print "Studio:", studio

theaters = get_movie_values(soup,'Foreign')
print "Theater:", theaters
