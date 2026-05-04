from bid_name_generator import random_bid_combo, random_single_bid
from helper import weighted, obfuscate_word, insert_noise_between_chars, random_case
from world_name_generator import random_world_name

try:
	from faker import Faker
except Exception:
	Faker = None


def install_negative_spam_grammar(gen):
	"""Install negative/benign examples that mirror positive shapes but are innocent.

	The goal is to produce messages similar in shape/distribution to the positive grammar
	but with non-commercial content (friends, invites, ownership) so ML can learn
	the difference.
	"""
	# Core token: same world name generator
	gen.add_rule("WORLD_NAME", random_world_name)

	# Person / owner tags (e.g., ME, MY, PLAYER names)
	PERSONS = weighted([
		("ME", 25),
		("MY", 30),
		("OUR", 8),
		("FRIEND", 6),
		("FRIENDS", 4),
		("PLAYER", 10),
		("SERVER", 5),
		("", 12),
	])

	def generate_person(rng):
		p = rng.choice(PERSONS)
		if not p:
			return ""
		# sometimes append a short number or small name part
		if rng.random() < 0.08:
			p = f"{p}{rng.randint(1,99)}"
		if rng.random() < 0.12:
			p = random_case(rng, p)
		return p

	gen.add_rule("PERSON", generate_person)

	def generate_person_obf(rng):
		p = generate_person(rng)
		if not p:
			return ""
		if rng.random() < 0.12:
			p = obfuscate_word(rng, p, p=0.12)
		return p

	gen.add_rule("PERSON_OBF", generate_person_obf)

	# Possessives and small connectors
	gen.add_rule("POSSESSIVE", weighted([
		("my", 70),
		("our", 10),
		("the", 10),
		("", 10),
	]))

	# Action verbs / invitation phrases (used as CTA-like for negative)
	ACTIONS = weighted([
		("go to", 30),
		("visit", 25),
		("join", 15),
		("come to", 10),
		("check out", 10),
		("play in", 10),
		("", 10),
	])

	def generate_action(rng):
		a = rng.choice(ACTIONS)
		if not a:
			return ""
		# rarely obfuscate or change case
		if rng.random() < 0.08:
			a = obfuscate_word(rng, a, p=0.08)
		if rng.random() < 0.1:
			a = random_case(rng, a)
		return a

	gen.add_rule("ACTION", generate_action)

	# Separators to match positive shapes but slightly fewer equals
	gen.add_rule("SEPARATOR", weighted([
		(" ", 50),
		(":", 20),
		("=", 10),
		("/", 10),
		("-", 10),
	]))

	# Tail punctuation
	gen.add_rule("TAIL", weighted([
		("", 80),
		("!", 10),
		(".", 8),
		("?", 2),
	]))

	# Templates mirrored to positive distribution but benign
	gen.add_rule("NONSPAM_MESSAGE", weighted([
		# canonical counterpart: PERSON SEPARATOR WORLD
		("{PERSON}{SEPARATOR}{WORLD_NAME}", 50),
		# space-separated (action + world)
		("{ACTION} {POSSESSIVE} {WORLD_NAME}", 20),
		# canonical with tail
		("{PERSON}{SEPARATOR}{WORLD_NAME}{TAIL}", 15),
		# CTA first (action) + canonical
		("{ACTION} {PERSON}{SEPARATOR}{WORLD_NAME}", 10),
		# slight obfuscation of person/owner
		("{PERSON_OBF}{SEPARATOR}{WORLD_NAME}", 15),
		# rare combo forms
		("{PERSON}/{PERSON} {WORLD_NAME}", 5),
		# reversed but benign
		("{WORLD_NAME}{SEPARATOR}{PERSON}", 5),
	]))

	# For convenience, also register a generic MESSAGE token to mirror SPAM_MESSAGE
	gen.add_rule("MESSAGE", weighted([
		("{NONSPAM_MESSAGE}", 100),
	]))

	return gen

def install_negative_spam_grammar_with_chat(gen):
	"""Install negative grammar but augment with realistic chat snippets using Faker if available.

	This keeps the distribution and token shapes similar to the positive grammar but includes
	more natural chat-like lines (e.g., "go to my world myworld32", short friendly invites).
	"""
	# First install the base negative grammar
	install_negative_spam_grammar(gen)

	rng = getattr(gen, 'rng', None)

	# Prepare faker if available
	faker = None
	if Faker is not None:
		faker = Faker()
		# try to seed faker if generator has a seed
		try:
			seed = getattr(gen, 'rng').seed
			faker.seed_instance(seed)
		except Exception:
			pass

	def generate_chat_snippet(rng_local):
		# Prefer short, natural fragments. Use Faker if present.
		if faker is not None and rng_local.random() < 0.8:
			# make a short user-style sentence with 3-6 words
			sent = faker.sentence(nb_words=rng_local.randint(3, 6))
			# strip trailing punctuation and shorten
			sent = sent.rstrip('.!')
			# Occasionally append a world name to mirror positive shapes
			if rng_local.random() < 0.35:
				sent = f"{sent} {random_world_name(rng_local)}"
			return sent

		# Fallback: build short benign phrases
		verbs = ["go to", "visit", "join", "come to", "check out", "play in"]
		targets = ["my world", "our world", "my server", "my place", "the event"]
		v = rng_local.choice(verbs)
		t = rng_local.choice(targets)
		# sometimes add a world name
		if rng_local.random() < 0.5:
			return f"{v} {t} {random_world_name(rng_local)}"
		return f"{v} {t}"

	gen.add_rule('CHAT_SNIPPET', generate_chat_snippet)

	# Add chat snippets into NONSPAM_MESSAGE distribution to increase natural negative examples
	# We'll insert a template that is purely a chat snippet and adjust other weights slightly
	# Read current rule and reweight by replacing NONSPAM_MESSAGE
	gen.add_rule("NONSPAM_MESSAGE", weighted([
		("{CHAT_SNIPPET}", 30),
		("{PERSON}{SEPARATOR}{WORLD_NAME}", 30),
		("{ACTION} {POSSESSIVE} {WORLD_NAME}", 15),
		("{PERSON}{SEPARATOR}{WORLD_NAME}{TAIL}", 10),
		("{ACTION} {PERSON}{SEPARATOR}{WORLD_NAME}", 8),
		("{PERSON_OBF}{SEPARATOR}{WORLD_NAME}", 10),
		("{PERSON}/{PERSON} {WORLD_NAME}", 3),
		("{WORLD_NAME}{SEPARATOR}{PERSON}", 4),
	]))

	return gen

