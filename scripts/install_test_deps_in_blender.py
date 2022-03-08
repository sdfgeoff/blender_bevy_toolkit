import ensurepip

ensurepip.bootstrap()

import pip

pip.main(["install", "vulture", "black", "pylint", "pytest"])
