"""Build the static reader from the authoritative HTML and accepted audio plans."""
import argparse,hashlib,html,json,re,shutil
from html.parser import HTMLParser
from pathlib import Path
from illustrations import externalize
from seo_metadata import metadata_html
from music_assets import export_music
from heading_revision import load_revision,apply_chapter,revision_metadata

parser=argparse.ArgumentParser();parser.add_argument('--web',type=Path);parser.add_argument('--source-root',type=Path);parser.add_argument('--revision-manifest',type=Path);args=parser.parse_args()
W=args.web or Path(__file__).resolve().parents[1]
N=args.source_root or W.parent;A=N/'Audiobook - Draft 2 - Expressive Cast'
heading_revision=load_revision(W,N,args.revision_manifest)
S=N/'2026-10-06-1423-sin-star-i-novel-draft-v1.html'
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
digest=lambda b:hashlib.sha256(b).hexdigest()
word_re=re.compile(r"[\w]+")
def words(s):return word_re.findall(s.replace('’',"'"))
def normalized(s):return ' '.join(words(s))
def save(path,data):path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')

class Annotate(HTMLParser):
    def __init__(self,chapter,segments):
        super().__init__(convert_charrefs=True);self.figure_depth=0;self.chapter=chapter;self.parts=[];self.tokens=[];self.output=[];self.block=0;self.word_offset=0;self.owners=[]
        for segment in segments:self.owners.extend([segment['id']]*len(words(segment['text'])))
        self.expected=[w for s in segments for w in words(s['text'])]
    def handle_starttag(self,tag,attrs):
        raw=self.get_starttag_text()
        if tag=='figure':self.figure_depth+=1
        if tag=='p' and not self.figure_depth:
            self.block+=1;raw=raw[:-1]+f' id="{self.chapter}-b{self.block:04d}" data-narratable="true">'
        self.output.append(raw)
    def handle_startendtag(self,tag,attrs):self.output.append(self.get_starttag_text())
    def handle_endtag(self,tag):
        self.output.append('</'+tag+'>')
        if tag=='figure':self.figure_depth-=1
    def handle_data(self,data):
        if self.figure_depth:self.output.append(html.escape(data,quote=False));return
        matches=list(word_re.finditer(data))
        if not matches:self.output.append(html.escape(data,quote=False));return
        actual=words(data);assert actual==self.expected[self.word_offset:self.word_offset+len(actual)],(self.chapter,self.word_offset,actual[:5])
        groups=[];start=0;owner=self.owners[self.word_offset]
        for i,match in enumerate(matches):
            next_owner=self.owners[self.word_offset+i]
            if next_owner!=owner:
                groups.append((owner,data[start:match.start()]));start=match.start();owner=next_owner
        groups.append((owner,data[start:]))
        for owner,text in groups:self.output.append(f'<span data-cue-id="{self.chapter}-s{owner:04d}">'+html.escape(text,quote=False)+'</span>')
        self.word_offset+=len(actual);self.tokens.extend(actual)

source=S.read_text(encoding='utf-8');sections=re.findall(r'<section\b.*?</section>',externalize(source,W),re.S);assert len(sections)==43
manifest=load(A/'release-manifest.json');mobile=load(A/'mobile/manifest.json')
W.mkdir(exist_ok=True);(W/'audio').mkdir(exist_ok=True);(W/'production').mkdir(exist_ok=True)
export_music(W,N.parents[1]/'Assets'/'Music')
title=W/'audio/title.mp3';assert title.is_file()
import subprocess
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(title)]))
chapters=[{'id':'titlepage','heading':'Title page','label':'Book One','title':'Sin Star','audio':'audio/title.mp3','bytes':title.stat().st_size,'sha256':digest(title.read_bytes()),'duration':float(probe['format']['duration']),'cues':[]}]
rendered=[sections[0].replace('class="titlepage"','class="titlepage reading-section"')]
for c,section in zip(manifest['chapters'],sections[1:]):
    n=c['index'];cid=f'ch-{n:02d}';plan=load(A/'plans'/f'{n:02d}.json')
    before,body=section.split('<div class="prose">',1)
    match=re.fullmatch(r'(.*)</div>(<nav class="chapterlinks".*</nav>)</section>',body,re.S);assert match
    body,footer=match.groups()
    annotated=Annotate(cid,plan['segments']);annotated.feed(body);assert annotated.tokens==annotated.expected
    section=before.replace('class="chapter"','class="chapter reading-section" hidden')+'<div class="prose">'+''.join(annotated.output)+'</div>'+footer+'</section>'
    rendered.append(section)
    audio=A/'mobile'/c['file'];record=next(r for r in mobile['chapters'] if r['file']==c['file']);assert digest(audio.read_bytes())==record['sha256']
    target=W/'audio'/f'{n:02d}.mp3'
    if not target.exists() or digest(target.read_bytes())!=record['sha256']:shutil.copy2(audio,target)
    cues=[]
    assert len(c['boundaries'])==len(plan['segments'])
    for seg,b in zip(plan['segments'],c['boundaries']):
        assert seg['id']==b['id'];text=normalized(seg['text'])
        cues.append({'id':f'{cid}-s{seg["id"]:04d}','start':b['start_seconds'],'end':b['end_seconds'],'text':text,'textHash':digest(text.encode())})
    label=re.search(r'<p class="label">(.*?)</p>',before,re.S).group(1);chapter_title=re.search(r'<h2[^>]*>(.*?)</h2>',before,re.S).group(1)
    chapters.append({'id':cid,'heading':c['heading'],'label':html.unescape(label),'title':html.unescape(chapter_title),'audio':f'audio/{n:02d}.mp3','bytes':target.stat().st_size,'sha256':record['sha256'],'duration':c['duration_seconds'],'cues':cues})
    rendered[-1]=apply_chapter(heading_revision,W,n,chapters[-1],rendered[-1])
nav=''.join(f'<li><a href="#{c["id"]}" data-chapter="{i}"><span class="nav-label">{html.escape(c["label"])}</span><span>{html.escape(c["title"])}</span><small class="offline-state" data-offline="{i}"></small></a></li>' for i,c in enumerate(chapters))
template='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#142b2b">__SEO_METADATA__<meta http-equiv="Content-Security-Policy" content="default-src 'self';script-src 'self';style-src 'self';img-src 'self' data:;media-src 'self' blob:;connect-src 'self';worker-src 'self';object-src 'none';base-uri 'self'"><link rel="stylesheet" href="./reader.css?v=20261008-music-five"><link rel="manifest" href="./manifest.webmanifest"><link rel="icon" href="./icon.svg" type="image/svg+xml"><script type="module" src="./app.js?v=20261008-music-five"></script></head><body>
<a class="skip" href="#reading">Skip to text</a><p id="passage-help" class="visually-hidden">Press Enter or Space to play this passage. Use Left and Right Arrow keys to choose another passage.</p><header class="topbar"><div class="header-left"><button id="contents-toggle" aria-label="Chapters" aria-controls="contents" aria-expanded="false">☰ <span>Chapters</span></button><button id="bookmarks-toggle" class="header-icon" aria-label="Bookmarks" title="Bookmarks" aria-controls="bookmarks" aria-expanded="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true" focusable="false"><path d="M6 3h12v18l-6-4-6 4z"/></svg></button></div><a class="brand" href="#titlepage" data-home>SIN STAR <span>BOOK ONE</span></a><div class="header-actions"><button id="downloads-toggle" class="header-icon" aria-label="Offline audio" title="Offline audio" aria-controls="downloads" aria-expanded="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M12 3v11m-4-4 4 4 4-4M5 15v5h14v-5"/></svg></button><a id="reader-home" class="header-icon" href="https://sincioco.com/" target="_top" aria-label="Home: Sincioco.com" title="Home: Sincioco.com"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="m3 10 9-7 9 7M5 9v12h5v-7h4v7h5V9"/></svg></a></div></header>
<aside id="contents" aria-label="Chapters"><p class="nav-eyebrow">THE COMPLETE NOVEL</p><nav><ol>__NAV__</ol></nav><p class="nav-footer">Created by Sin<br>5 hours · 42 chapters</p></aside>
<main id="reading" tabindex="-1">__CONTENT__</main>
<section id="downloads" class="download-panel" aria-labelledby="downloads-title" hidden><div class="panel-heading"><h2 id="downloads-title">Listen offline</h2><button id="downloads-close" aria-label="Close offline panel">×</button></div><p>Keep audio in this browser on this device. It plays the local copy first. Your browser may clear stored audio; these are separate from your phone’s Downloads folder.</p><p id="storage-status" role="status">Checking offline support…</p><div class="download-actions"><button id="download-current">Download this chapter</button><button id="download-all">Download whole book</button><button id="download-cancel" hidden>Cancel download</button></div><progress id="download-progress" max="1" value="0" hidden aria-label="Audio download progress"></progress><p id="download-status" role="status"></p><div class="download-actions secondary"><button id="remove-current">Remove this chapter</button><button id="remove-all">Remove all offline audio</button></div><hr><h3>Background music (optional)</h3><p class="fine-print">Chapter downloads include narration only. Save these three tracks separately for offline music. Music never blocks narration. Removing copies does not stop tracks already in memory.</p><p id="music-storage-status" role="status">Checking saved music.</p><div class="download-actions"><button id="music-download" disabled>Download music</button><button id="music-cancel" hidden>Cancel music download</button><button id="music-remove">Remove saved music</button></div><a id="save-file" download>Save this MP3 to Files</a><p class="fine-print">These chapter downloads include the spoken section label and title. Keep this page open while downloading. Check chapter badges before going offline. HTTPS is required when deployed.</p></section>
<section id="bookmarks" class="download-panel bookmark-panel" aria-labelledby="bookmarks-title" hidden>
<div class="panel-heading"><h2 id="bookmarks-title">Bookmarks</h2><button id="bookmark-close" aria-label="Close bookmarks">×</button></div>
<p id="bookmark-status" role="status"></p>
<details id="bookmark-composer" class="bookmark-draft"><summary>Bookmark selected or spoken text</summary><blockquote id="bookmark-quote"></blockquote><p id="bookmark-match" class="fine-print"></p>
<label for="bookmark-note">Note (optional)</label><textarea id="bookmark-note" rows="3" maxlength="10000" placeholder="Your thoughts about this passage"></textarea><button id="bookmark-save" disabled>Bookmark selection</button></details>
<h3>Saved bookmarks</h3><ol id="bookmark-list"></ol></section>
<footer class="player" aria-label="Audiobook player"><div class="now-playing"><span class="player-eyebrow">NOW READING</span><strong id="current-title">Title page</strong><span id="playback-status" role="status">Loading the book…</span></div><div class="transport"><button id="previous" aria-label="Previous chapter">← <span>Previous</span></button><button id="play" class="primary" aria-label="Play audio">Play</button><button id="next" aria-label="Next chapter"><span>Next</span> →</button></div><div class="timeline"><span id="elapsed">0:00</span><input id="seek" type="range" min="0" max="1" step="0.1" value="0" aria-label="Playback position"><span id="duration">0:00</span></div><div class="reading-options"><label><input id="follow" type="checkbox" autocomplete="off" checked> Follow narration</label><button id="text-smaller" aria-label="Smaller text">A−</button><button id="text-larger" aria-label="Larger text">A+</button><span id="connection-status"></span></div><button id="music-toggle" class="music-toggle" aria-label="Music settings" title="Music settings" aria-controls="music-panel" aria-haspopup="dialog" aria-expanded="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M14 18V4l6 3"/><ellipse cx="10" cy="18" rx="4" ry="3"/></svg></button><audio id="audio" preload="metadata"></audio></footer>
<dialog id="music-panel" class="music-panel" aria-labelledby="music-panel-title" aria-describedby="music-help">
<div class="panel-heading"><h2 id="music-panel-title">Background music</h2><button id="music-close" type="button" aria-label="Close music settings">×</button></div>
<p id="music-help">Enable music prepares it. Press Play in the audiobook player to hear music with narration; both pause together.</p>
<div class="music-row"><label for="music-volume">Volume</label><input id="music-volume" type="range" min="0" max="10" step="1" value="5" aria-label="Music volume"><output id="music-level" for="music-volume">5%</output></div>
<div class="music-actions"><button id="music-mute" aria-pressed="false">Mute</button><button id="music-enable" title="Enable or resume music after browser interruption">Enable music</button></div>
<p id="music-status" role="status">Music follows narration</p></dialog>
<noscript><p class="noscript">Enable JavaScript for audio controls and chapter navigation.</p></noscript></body></html>'''
(W/'index.html').write_text(template.replace('__SEO_METADATA__',metadata_html()).replace('__NAV__',nav).replace('__CONTENT__','\n'.join(rendered)),encoding='utf-8')
# Presentation changes retain existing downloaded audio and listening positions.
media_signature=lambda records:json.dumps([{key:c[key] for key in ('id','sha256','bytes','duration','cues')} for c in records],sort_keys=True)
signature=media_signature(chapters)
previous=load(W/'book.json') if (W/'book.json').exists() else None
revision=previous['version'] if previous and previous['manuscriptSha256']==manifest['source_sha256'] and media_signature(previous['chapters'])==signature else digest(('audio-v1|'+signature).encode())[:16]
book={'version':revision,'identity':'sin-star-book-one-'+manifest['source_sha256'][:16],'sourceHtmlSha256':digest(S.read_bytes()),'manuscriptSha256':manifest['source_sha256'],'titleSpeech':'Sin Star. Book One. Created by Sin.','alignment':'Exact production chunk boundaries; phrase/paragraph highlighting, not word-level timing. Unmatched or edited cues are cleared.','chapters':chapters,'totalBytes':sum(c['bytes'] for c in chapters)}
book.update(revision_metadata(heading_revision))
save(W/'book.json',book)
save(W/'manifest.webmanifest',{'name':'Sin Star · Book One','short_name':'Sin Star','start_url':'./','scope':'./','display':'standalone','background_color':'#f5f1e8','theme_color':'#142b2b','icons':[{'src':'./icon.svg','sizes':'any','type':'image/svg+xml','purpose':'any'}]})
(W/'icon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 192 192"><rect width="192" height="192" rx="38" fill="#142b2b"/><path d="m96 28 15 48 50 1-40 30 14 48-39-28-40 28 15-48-40-30 50-1Z" fill="#dbc58d"/></svg>',encoding='utf-8')
save(W/'production/build-report.json',{'source_html_sha256':digest(S.read_bytes()),'source_markdown_sha256':manifest['source_sha256'],'chapter_audio_count':42,'title_audio_count':1,'audio_bytes':book['totalBytes'],'aligned_chunks':sum(len(c['cues']) for c in chapters),'unmatched_chunks':0,'exact_narrative_tokens_verified':True,'source_html_unchanged':True,'mobile_audio_copies_sha_verified':42,'cue_strategy':book['alignment']})
import runpy
runpy.run_path(str(W/'production/refresh_cache.py'),init_globals={'WEB_ROOT':W})
print(json.dumps({'web':str(W),'version':revision,'audio_bytes':book['totalBytes'],'cues':sum(len(c['cues']) for c in chapters)}))
