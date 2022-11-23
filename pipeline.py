import cv2
from modules.midi_converter import MidiConverter
from modules.video_config import VideoConfig
from multiprocessing import Process, Queue
import queue


config = VideoConfig.from_yaml("config.yaml")
midi_converter = MidiConverter(config, generate_masks=True)

def worker(q_in, q_out):
	results = []
	while True:
		try:
			frame_num, frame = q_in.get(block=True, timeout=1)
			# with count.get_lock():
			# 	count.value -= 1
		except queue.Empty:
			print("Exitting")
			q_out.put(results)
			return # probably done
		results.append((frame_num, midi_converter.process_frame_arg(frame)))
		print(f"{frame_num}")

def video_acquire(q):
	cap = cv2.VideoCapture("Downloads/Speech Bubbles - The Smile [Piano Cover].mp4")
	while True:
		frame_num = cap.get(cv2.CAP_PROP_POS_FRAMES)
		grabbed, frame = cap.read()
		if not grabbed:
			return
		# with count.get_lock():
		# 	count.value += 1
		q.put((frame_num, frame))


if __name__ == '__main__':
	pq = queue.PriorityQueue()
	frame_num=0
	q = Queue(maxsize=10)
	qs = [Queue() for _ in range(9)]
	# count = Value('i', 0)
	acq = Process(target=video_acquire, args=(q,))
	ps= [(Process(target=worker, args=(q,qs[i])), qs[i]) for i in range(9)]
	acq.start()
	for p,_ in ps:
		p.start()
	acq.join()
	print("acq joined")
	results = []
	for p,q_out in ps:
		for item in q_out.get():
			pq.put(item)
		p.join()
		print("p joined")
	while True:
		try:
			frame_num, keys_pressed = pq.get(block=False)
		except Exception:
			break
		midi_converter.update_state(keys_pressed, frame_num)
	midi_converter.save("song.mid")