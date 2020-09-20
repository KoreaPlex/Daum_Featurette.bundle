#Plex Theme Music
import unicodedata
import re, time, unicodedata, hashlib, types , random
THEME_URL = 'https://tvthemes.plexapp.com/%s.mp3'
try:
  server_url = Prefs['server_url']
  if Prefs['server_url'] != "" and Prefs['server_url'][-1] == '/':
    Log('Server Url has an error. correct it : %s' % server_url)
    server_url = Prefs['server_url'][:-1]
except:
  server_url = 'http://103.208.222.5:23456'

def Start():
  HTTP.CacheTime = None
  HTTP.Headers[
    'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
  HTTP.Headers['Accept-Language'] = 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'


TYPE_ORDER = ['primary_trailer', 'trailer', 'behind_the_scenes', 'interview', 'scene_or_sample']
EXTRA_TYPE_MAP = {'primary_trailer' : TrailerObject,
                  'trailer' : TrailerObject,
                  'interview' : InterviewObject,
                  'behind_the_scenes' : BehindTheScenesObject,
                  'scene_or_sample' : SceneOrSampleObject}

EXTRA_TYPE_MAP = {'trailer' : TrailerObject,
                'deleted' : DeletedSceneObject,
                'behindthescenes' : BehindTheScenesObject,
                'behind_the_scenes' : BehindTheScenesObject,
                'interview' : InterviewObject,
                'scene' : SceneOrSampleObject,
                'featurette' : FeaturetteObject,
                'short' : ShortObject,
                'other' : OtherObject,
                'extra' : OtherObject,
                'scene_or_sample' :SceneOrSampleObject }

def make_style(text):
  if text.count('인터뷰') > 0 : return 'interview' # 2
  if text.count('티저') > 0 : return 'trailer' # 1
  if text.count('스페셜') > 0 : return 'behind_the_scenes'
  if text.count('예고') > 0 : return 'trailer' # 1
  if text.count('삭제') > 0: return 'deleted'  # 2
  if text.count('부가') > 0: return 'featurette'  # 2
  if text.lower().count('m/v') > 0: return 'featurette' # 장면
  if text.lower().count('mv') > 0: return 'featurette'  # 장면
  if text.lower().count('ost') > 0: return 'featurette'  # 장면
  if text.lower().count('soundtrack') > 0: return 'scene_or_sample'  # 장면
  return 'scene_or_sample' # 메이킹

def scrub_extra(extra, media_title):
  e = extra['extra']
  # Remove the "Movie Title: " from non-trailer extra titles.
  if media_title is not None:
    r = re.compile(media_title + ': ', re.IGNORECASE)
    e.title = r.sub('', e.title)
  # Remove the "Movie Title Scene: " from SceneOrSample extra titles.
  if media_title is not None:
    r = re.compile(media_title + ' Scene: ', re.IGNORECASE)
    e.title = r.sub('', e.title)

  # Capitalise UK correctly.
  e.title = e.title.replace('Uk', 'UK')

  return extra


class DaumFeaturette(Agent.TV_Shows):
  name = 'Daum 부가영상'
  languages = [Locale.Language.NoLanguage]
  primary_provider = False
  accepts_from = ['com.plexapp.agents.localmedia', 'com.plexapp.agents.sj_daum']
  contributes_to = ['com.plexapp.agents.sj_daum']
  def search(self, results, media, lang):
    Log(media.primary_agent)
    self.genres = []
    if  media.primary_agent in ['com.plexapp.agents.sj_daum']:
      Log(str(media.primary_metadata.id))
      self.genres = [str(item) for item in media.primary_metadata.genres]
      results.Append(MetadataSearchResult(
        id=media.primary_metadata.id,
        score=100
      ))

  def update(self, metadata, media, lang, force=False):
    # k_movie://cdn.discordapp.com/attachments/750218451540377601/751781342978769026/1599140046.015252.mp4
    Log(str(media.title))
    Log(str(metadata.title))
    try:
      tmp = JSON.ObjectFromURL(server_url + '/drama_trailer', values=dict(metadata_id=metadata.id , cacheTime=0 ,apikey = Prefs['apikey']))['result']
    except:
      tmp = None
      pass
    extras = []
    if tmp:
      for extra in tmp:
        style = make_style(extra['title'])
        if Prefs['trailer_location'] == 'Proxy':
            tmpurl = extra['attachments']['proxy_url']
        elif Prefs['trailer_location'] == "CDN":
            tmpurl = extra['attachments']['url']
        if style == "trailer":
          try:thumb = extra['thumb']
          except:thumb= ""
          extras.append({'type': EXTRA_TYPE_MAP[style],
                         'lang': 'ko',
                         'extra': EXTRA_TYPE_MAP[style](
                           #url='k_movie://cdn.discordapp.com/attachments/750218451540377601/751781342978769026/1599140046.015252.mp4',
                           url='k_movie://' + tmpurl.replace('https://', ''),
                           title=extra['title'].strip(),
                           #originally_available_at=avail,
                           thumb= thumb)})
      for extra in tmp:
        style = make_style(extra['title'])
        if style in ["interview",'deleted','featurette' ]:
          try:thumb = extra['thumb']
          except:thumb= ""
          extras.append({'type': EXTRA_TYPE_MAP[style],
                         'lang': 'ko',
                         'extra': EXTRA_TYPE_MAP[style](
                           #url='k_movie://cdn.discordapp.com/attachments/750218451540377601/751781342978769026/1599140046.015252.mp4',
                           url='k_movie://' + tmpurl.replace('https://', ''),
                           title=extra['title'].strip(),
                           #originally_available_at=avail,
                           thumb= thumb)})
      for extra in tmp:
        style = make_style(extra['title'])
        if style not in ["trailer" , "interview",'deleted','featurette' ]:
          try:thumb = extra['thumb']
          except:thumb= ""
          extras.append({'type': EXTRA_TYPE_MAP[style],
                         'lang': 'ko',
                         'extra': EXTRA_TYPE_MAP[style](
                           #url='k_movie://cdn.discordapp.com/attachments/750218451540377601/751781342978769026/1599140046.015252.mp4',
                           url='k_movie://' + extra['attachments']['url'].replace('https://', ''),
                           title=extra['title'].strip(),
                           #originally_available_at=avail,
                           thumb= thumb)})
      for extra in tmp:
        style = make_style(extra['title'])
        if style == "scene_or_sample":
          try:thumb = extra['thumb']
          except:thumb= ""
          extras.append({'type': EXTRA_TYPE_MAP[style],
                         'lang': 'ko',
                         'extra': EXTRA_TYPE_MAP[style](
                           #url='k_movie://cdn.discordapp.com/attachments/750218451540377601/751781342978769026/1599140046.015252.mp4',
                           url='k_movie://' + extra['attachments']['url'].replace('https://', ''),
                           title=extra['title'].strip(),
                           #originally_available_at=avail,
                           thumb= thumb)})

    extras = [scrub_extra(extra, extra.get('title')) for extra in extras]
    # Add them in the right order to the metadata.extras list.
    for extra in extras:
      metadata.extras.add(extra['extra'])

