try:
    from attribute_plugin import add_test_properties  # type: ignore[import-untyped]
except ImportError:
    # Define no-op decorator if attribute_plugin is not available (outside bazel)
    # Keeps IDE debugging functionality
    def add_test_properties(*args, **kwargs):
        def decorator(func):
            return func  # No-op decorator

        return decorator
