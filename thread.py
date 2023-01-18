from __future__ import annotations
import concurrent.futures
import inspect
from typing import Callable, Dict, List, Any, Iterable
from collections.abc import Iterable


class Thread:
    def __init__(self, callback:Callable, kwargs:Iterable[Dict[Any, Any]], max_workers: int = 5) -> None:
        assert isinstance(kwargs, Iterable), f"{kwargs} is not iterable type"
        
        self.callback = callback
        self.kwargs = kwargs
        self.max_workers = max_workers
    
    def _create_callback(self, **kwargs) -> Callable:
        return lambda : self.callback(**kwargs)
    
    def _generate_callbacks(self) -> List[Callable]:
        return [self._create_callback(**kwargs) for kwargs in self.kwargs]
    
    def execute(self) -> List[Any]:
        callbacks = self._generate_callbacks()
        with concurrent.futures.ThreadPoolExecutor(max_workers= self.max_workers) as exe:
            futures = [ exe.submit(callback) for callback in callbacks ]
            
            return [future.result() for future in concurrent.futures.as_completed(futures)]
    
    def map(self) -> List[Any]:
        callbacks = self._generate_callbacks()
        with concurrent.futures.ThreadPoolExecutor() as exe:
            futures = [ exe.submit(callback) for callback in callbacks ]
            
            return [future.result() for future in futures]
    
                
    def __repr__(self) -> str:
        return "\n".join([
            f"Callback:\n{inspect.getsource(self.callback)}",
            f"Arguments To Be Subbmitted: {self.kwargs}"
        ])