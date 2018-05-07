module Fields
  class TestCase < Base
    def initialize(fields_str, override_default_fields = nil)
      super(fields_str, override_default_fields)
    end

    def default_fields
      [:uuid, :input, :output]
    end

    def serializer
      TestCaseSerializer
    end
  end
end