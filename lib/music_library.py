import lxml.etree as ET

KEY_NODE_TYPE = "Type"
KEY_PLAYLIST_ENTRIES = "Entries"

NODE_TYPE_FOLDER = "0"
NODE_TYPE_PLAYLIST = "1"

class MusicLibrary:
	def __init__(self, fileName: str):
		with open(fileName, "r") as inFile:
			self.xml = ET.parse(inFile)

		self.collection = {track.get("TrackID"): track.attrib for track in self.xml.findall("./COLLECTION/TRACK")}
		self.playlists = {}

		playlist_root = self.xml.find("./PLAYLISTS/NODE[1]")

		for item in playlist_root.iter("NODE"):
			if item == playlist_root:
				continue

			data = dict(item.attrib)

			if data[KEY_NODE_TYPE] == NODE_TYPE_PLAYLIST:
				data[KEY_PLAYLIST_ENTRIES] = [track.get("Key") for track in item.findall("TRACK")]

			playlist_path = MusicLibrary.__compute_playlist_path(playlist_root, item)
			self.playlists[playlist_path] = data

	def playlist_paths(self):
		return self.playlists.keys()

	def playlist_track_ids(self, playlist_path: str):
		if playlist_path not in self.playlists:
			raise KeyError(f"No playlist with path {playlist_path}")

		return self.playlists[playlist_path][KEY_PLAYLIST_ENTRIES]

	def playlist_tracks(self, playlist_path: str):
		return self.tracks_by_id(self.playlist_track_ids(playlist_path), True)

	def tracks_by_id(self, track_ids: list, must_exist: bool = True):
		tracks = []
		ids_not_found = []

		for id in track_ids:
			if id not in self.collection:
				ids_not_found.append(id)
				continue

			tracks.append(self.collection[id])

		if must_exist and ids_not_found:
			raise KeyError("The following track IDs were not found: " + (", ".join(ids_not_found)))

		return tracks

	def __compute_playlist_path(root, item):
		path = ""

		while item != root:
			name = item.get('Name').replace('|', '_')
			path = f"{name}|{path}" if path else name
			item = item.getparent()

		return path
