# -*- coding: utf-8 -*-
"""
线程锁
"""
from . import utils
from . import constants
from . import exceptions
from . import portalocker

#: Exception thrown when the file is already locked by someone else
AlreadyLocked = exceptions.AlreadyLocked
#: Exception thrown if an error occurred during locking
LockException = exceptions.LockException

#: Lock a file. Note that this is an advisory lock on Linux/Unix systems
lock = portalocker.lock
#: Unlock a file
unlock = portalocker.unlock

#: Place an exclusive lock.
#: Only one process may hold an exclusive lock for a given file at a given
#: time.
LOCK_EX = constants.LOCK_EX

#: Place a shared lock.
#: More than one process may hold a shared lock for a given file at a given
#: time.
LOCK_SH = constants.LOCK_SH

#: Acquire the lock in a non-blocking fashion.
LOCK_NB = constants.LOCK_NB

#: Remove an existing lock held by this process.
LOCK_UN = constants.LOCK_UN

#: Locking utility class to automatically handle opening with timeouts and
#: context wrappers
Lock = utils.Lock
RLock = utils.RLock
TemporaryFileLock = utils.TemporaryFileLock
open_atomic = utils.open_atomic

__all__ = [
    'lock',
    'unlock',
    'LOCK_EX',
    'LOCK_SH',
    'LOCK_NB',
    'LOCK_UN',
    'LockException',
    'Lock',
    'AlreadyLocked',
    'open_atomic',
]
