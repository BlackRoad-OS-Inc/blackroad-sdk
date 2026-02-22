"""
BlackRoad Tasks API
"""

from typing import Optional, Dict, Any, List


class TaskAPI:
    """
    Task management API for the 30K agent infrastructure.

    Usage:
        # Dispatch a task
        task = client.tasks.dispatch(
            title="Deploy authentication service",
            description="Deploy Keycloak to Security division",
            priority="urgent",
            division="Security"
        )

        # Get task status
        task = client.tasks.get(task["task_id"])

        # Complete a task
        client.tasks.complete(task["task_id"], result="Deployed successfully")

        # List pending tasks
        pending = client.tasks.list(status="pending")
    """

    def __init__(self, client):
        self._client = client

    def dispatch(
        self,
        title: str,
        description: Optional[str] = None,
        priority: str = "medium",
        division: Optional[str] = None,
        target_level: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Dispatch a new task to the agent hierarchy.

        Args:
            title: Task title
            description: Detailed description
            priority: Priority level (urgent, high, medium, low)
            division: Target division (OS, AI, Security, etc.)
            target_level: Target hierarchy level (2=commanders, 3=managers, 4=workers)
            metadata: Additional task metadata

        Returns:
            Created task dictionary with task_id
        """
        data = {
            "title": title,
            "priority": priority
        }
        if description:
            data["description"] = description
        if division:
            data["division"] = division
        if target_level:
            data["target_level"] = target_level
        if metadata:
            data["metadata"] = metadata

        return self._client.post("/tasks", data=data)

    def get(self, task_id: str) -> Dict[str, Any]:
        """Get a specific task by ID."""
        return self._client.get(f"/tasks/{task_id}")

    def list(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        division: Optional[str] = None,
        assigned_agent: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List tasks with optional filters.

        Args:
            status: Filter by status (pending, assigned, in_progress, completed, failed)
            priority: Filter by priority
            division: Filter by division
            assigned_agent: Filter by assigned agent
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of task dictionaries
        """
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        if priority:
            params["priority"] = priority
        if division:
            params["division"] = division
        if assigned_agent:
            params["assigned_agent"] = assigned_agent

        return self._client.get("/tasks", params=params).get("tasks", [])

    def complete(self, task_id: str, result: Optional[str] = None) -> Dict[str, Any]:
        """
        Mark a task as completed.

        Args:
            task_id: Task ID
            result: Result summary

        Returns:
            Updated task
        """
        data = {"status": "completed"}
        if result:
            data["result"] = result

        return self._client.put(f"/tasks/{task_id}", data=data)

    def fail(self, task_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Mark a task as failed.

        Args:
            task_id: Task ID
            reason: Failure reason

        Returns:
            Updated task
        """
        data = {"status": "failed"}
        if reason:
            data["result"] = reason

        return self._client.put(f"/tasks/{task_id}", data=data)

    def assign(self, task_id: str, agent_id: str) -> Dict[str, Any]:
        """
        Assign a task to a specific agent.

        Args:
            task_id: Task ID
            agent_id: Agent ID to assign

        Returns:
            Updated task
        """
        return self._client.put(f"/tasks/{task_id}", data={
            "assigned_agent": agent_id,
            "status": "assigned"
        })

    def cancel(self, task_id: str) -> Dict[str, Any]:
        """Cancel a pending task."""
        return self._client.delete(f"/tasks/{task_id}")

    def stats(self) -> Dict[str, Any]:
        """Get task statistics."""
        return self._client.get("/tasks/stats")

    def pending(self) -> List[Dict[str, Any]]:
        """Get all pending tasks."""
        return self.list(status="pending")

    def in_progress(self) -> List[Dict[str, Any]]:
        """Get all in-progress tasks."""
        return self.list(status="in_progress")

    def by_division(self, division: str) -> List[Dict[str, Any]]:
        """Get all tasks for a division."""
        return self.list(division=division)

    def urgent(self) -> List[Dict[str, Any]]:
        """Get all urgent tasks."""
        return self.list(priority="urgent")
