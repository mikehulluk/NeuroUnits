



namespace mhbuffer
{

    template<typename T, size_t SZ>
    class array
    {
        T _data[SZ];
    public:
        T& operator[](size_t i) { return _data[i]; }
        size_t size(){ return SZ;}
    };



};
