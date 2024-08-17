"""
Created on 2024-08-13

@author: wf
"""

from dataclasses import dataclass

import sprinkler


@dataclass
class Version(object):
    """
    Version handling for nicesprinkler
    """

    name = "nicesprinkler"
    version = sprinkler.__version__
    date = "2024-08-13"
    updated = "2024-08-10"
    description = "Computer Controlled 2 Stepper motor 3D lawn sprinkler system"

    authors = "Wolfgang Fahl"

    doc_url = "https://wiki.bitplan.com/index.php/nicesprinkler"
    chat_url = "https://github.com/WolfgangFahl/nicesprinkler/discussions"
    cm_url = "https://github.com/WolfgangFahl/nicesprinkler"

    license = f"""Copyright 2024 contributors. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied."""
    longDescription = f"""{name} version {version}
{description}

  Created by {authors} on {date} last updated {updated}"""
