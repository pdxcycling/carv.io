## YouTube Exploration
## Good reference: https://developers.google.com/youtube/v3/docs/search/list
from apiclient.errors import HttpError
from apiclient.discovery import build
import pandas as pd

## TODO: Don't check this in!!!
## Structure of returned data:
## results[video_id]['video']
##                  ['stats']
##                  ['comments']
##                  ['']
## TODO: The parts we want to access: snippet,contentDetails,statistics,status,topicDetails,localizations
## TODO: The duration of the video is in ISO8601 format. Yay for standards!

class YouTubeScraper(object):
    DEVELOPER_KEY = "AIzaSyAVJTKFIbA9AY5PG5ZAPugd9Exmhj_hV6s"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    def __init__(self):
        '''
        Constructor
        '''
        self.youtube = build( YouTubeScraper.YOUTUBE_API_SERVICE_NAME,
                              YouTubeScraper.YOUTUBE_API_VERSION,
                              developerKey=YouTubeScraper.DEVELOPER_KEY
                            )

    def search(self, query, max_results=500):
        '''
        Run search query
        '''
        #query = 'gopro,snowboarding'
        query = query
        num_results = 0
        result_list = []
        next_page_token = None
        while num_results < max_results:
            print "Retrieving results " + str(num_results+1) + " to " + str(num_results + 50)
            print "from " + str(next_page_token)
            if next_page_token:
                results = self.youtube.search().list(
                                    type='video',
                                    part="id,snippet",
                                    q=query,   ## query term(s)
                                    videoDuration='short',
                                    videoLicense='any', ## can set this to creative commons should i want...
                                    order='viewCount',
                                    pageToken=next_page_token, ## Only when it exists...
                                    maxResults='50'
                                  ).execute()
            else:
                results = self.youtube.search().list(
                                    type='video',
                                    part="id,snippet",
                                    q=query,   ## query term(s)
                                    videoDuration='short',
                                    videoLicense='any', ## can set this to creative commons should i want...
                                    order='viewCount',
                                    maxResults='50'
                                  ).execute()
            ## Parse/Store the results
            result_list.append(results.copy())
            ## Get next page
            num_results += results['pageInfo']['resultsPerPage']
            if 'nextPageToken' in results:
                next_page_token = results['nextPageToken']
            else:
                break

        ## Note: the nextPageToken in the results can be used to retrieve the next page of results
        return result_list
        ## Then look up the comments, likes, dislikes for each of the returned pages

    # Call the API's commentThreads.list method to list the existing comments.
    def get_comment_threads(self, youtube, video_id):
        '''
        Based on Google API's Python example
        INPUTS:
        OUTPUT:
        '''
        results = self.youtube.commentThreads().list(
                        part="snippet",
                        videoId=video_id,
                        textFormat="plainText"
                      ).execute()

        for item in results["items"]:
            comment = item["snippet"]["topLevelComment"]
            author = comment["snippet"]["authorDisplayName"]
            text = comment["snippet"]["textDisplay"]
            print "Comment by %s: %s" % (author, text)

        return results["items"]

    def to_dataframe(self, results):
        video_stats = pd.DataFrame()
        iteration  = 0
        yts = YouTubeScraper()
        for r in results:
            for item in r['items']:
                #print "Iteration " + str(iteration)
                v_id = item['id']['videoId']
                #video_stats = video_stats.append(pd.DataFrame([v_id], columns=['id']))
                stats = pd.DataFrame()
                stats = yts.get_video_stats(v_id)
                stats['id'] = v_id
                video_stats = video_stats.append(stats)
                iteration += 1
        video_stats = video_stats.reset_index().drop('index', axis=1)
        return video_stats

    def get_video_stats(self, video_id, verbose=False):
        '''
        Based on Google API's Python example
        Return pandas dataframe of
        '''
        results = self.youtube.videos().list(
                    part="snippet,contentDetails,statistics,status,topicDetails,localizations",
                    id=video_id
                    ).execute()

        # The localized object contains localized text if the hl parameter specified
        # a language for which localized text is available. Otherwise, the localized
        # object will contain metadata in the default language.
        stats = results["items"][0]["statistics"]
        viewCount = stats["viewCount"]
        if 'likeCount' in stats:
            likeCount = stats["likeCount"]
        else:
            likeCount = ''
            print "Debug: ", stats

        if 'dislikeCount' in stats:
            dislikeCount = stats["dislikeCount"]
        else:
            dislikeCount = ''
            print "Debug: ", stats

        if 'favoriteCount' in stats:
            favoriteCount = stats["favoriteCount"]
        else:
            favoriteCount = ''
            print "Debug: ", stats

        if 'commentCount' in stats:
            commentCount = stats["commentCount"]
        else:
            commentCount = ''
            print "Debug: ", stats

        ## Google API part: snippet
        snippet = results["items"][0]["snippet"]
        date = snippet["publishedAt"]
        title = snippet["title"]
        description = snippet["description"]

        ## Google API part: contentDetails
        details = results["items"][0]["contentDetails"]
        duration = details["duration"]

        output = pd.DataFrame(index=[0])
        output['viewCount'] = viewCount
        output['likeCount'] = likeCount
        output['dislikeCount'] = dislikeCount
        output['favoriteCount'] = favoriteCount
        output['commentCount'] = commentCount
        output['date'] = date
        output['title'] = title
        output['description'] = description
        output['duration'] = duration
        return output
